"""
Celery tasks for running event scrapers.
"""

import asyncio
import logging
import time
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.city import City
from app.db.models.source import Source
from app.db.models.sync_log import SyncLog
from app.services.scrapers import SCRAPER_REGISTRY
from app.worker import celery_app, get_sync_engine

logger = logging.getLogger("what2do.worker")


def _get_sync_session() -> Session:
    """Create a sync SQLAlchemy session for Celery tasks."""
    engine = get_sync_engine()
    return Session(engine)


@celery_app.task(name="scrape_all", autoretry_for=(Exception,), retry_backoff=60, max_retries=2)
def scrape_all_task() -> dict:
    """Run all active scrapers sequentially, logging results."""
    logger.info("Starting scrape_all_task")
    results = {}

    with _get_sync_session() as session:
        sources = session.execute(
            select(Source).where(Source.is_active.is_(True))
        ).scalars().all()

        for source in sources:
            if source.name in SCRAPER_REGISTRY:
                result = _run_single_scraper(session, source)
                results[source.name] = result
            else:
                logger.warning("No scraper registered for source: %s", source.name)

    logger.info("scrape_all_task complete: %s", results)
    return results


@celery_app.task(name="scrape_source")
def scrape_source_task(source_name: str, city_slug: str = "dallas") -> dict:
    """Run a single scraper by source name."""
    logger.info("Starting scrape_source_task for %s", source_name)

    if source_name not in SCRAPER_REGISTRY:
        msg = f"Unknown scraper: {source_name}"
        logger.error(msg)
        return {"error": msg}

    with _get_sync_session() as session:
        source = session.execute(
            select(Source).where(Source.name == source_name)
        ).scalar_one_or_none()

        if source is None:
            msg = f"Source not found in DB: {source_name}"
            logger.error(msg)
            return {"error": msg}

        return _run_single_scraper(session, source)


def _run_single_scraper(session: Session, source: Source) -> dict:
    """Execute a scraper and record results in a SyncLog."""
    start_time = time.time()

    # Get scraper and city first
    scraper_cls = SCRAPER_REGISTRY[source.name]
    scraper = scraper_cls()
    city = session.execute(
        select(City).where(City.slug == scraper.city_slug)
    ).scalar_one_or_none()

    # Create sync log entry with city_id
    sync_log = SyncLog(
        source_id=source.id,
        city_id=city.id if city else None,
        action="scrape",
        status="started",
    )
    session.add(sync_log)
    session.commit()

    try:
        if city is None:
            raise RuntimeError(f"City not found for slug: {scraper.city_slug}")

        from app.services.deduplicator import deduplicate_and_store
        from app.services.embedder import embed_events
        from app.core.config import get_settings
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

        async def _scrape_and_dedup():
            scraped_events = await scraper.scrape()
            # Create a fresh async engine each time to avoid event loop binding issues
            _settings = get_settings()
            _engine = create_async_engine(_settings.ASYNC_DATABASE_URL)
            _session_factory = async_sessionmaker(_engine, class_=AsyncSession, expire_on_commit=False)
            try:
                async with _session_factory() as db:
                    counts = await deduplicate_and_store(
                        db, scraped_events, source.id, city.id
                    )
                # Embed newly created events in a separate session
                async with _session_factory() as db:
                    embedded = await embed_events(db)
                    counts["embedded"] = embedded
                return counts
            finally:
                await _engine.dispose()

        counts = asyncio.run(_scrape_and_dedup())

        # Update sync log
        duration = time.time() - start_time
        sync_log.status = "completed"
        sync_log.events_found = counts["found"]
        sync_log.events_created = counts["created"]
        sync_log.events_updated = counts["updated"]
        sync_log.events_deduplicated = counts["deduplicated"]
        sync_log.duration_seconds = duration
        sync_log.completed_at = datetime.now(timezone.utc)

        # Update source last_scraped_at
        source.last_scraped_at = datetime.now(timezone.utc)

        session.commit()

        logger.info(
            "Scraper %s completed in %.1fs: %s", source.name, duration, counts
        )
        return counts

    except Exception as exc:
        duration = time.time() - start_time
        sync_log.status = "failed"
        sync_log.error = str(exc)[:2000]
        sync_log.duration_seconds = duration
        sync_log.completed_at = datetime.now(timezone.utc)
        session.commit()

        logger.exception("Scraper %s failed after %.1fs", source.name, duration)
        return {"error": str(exc)}
