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


@celery_app.task(name="scrape_all")
def scrape_all_task() -> dict:
    """Run all active scrapers sequentially, logging results."""
    logger.info("Starting scrape_all_task")
    results = {}

    with _get_sync_session() as session:
        sources = session.execute(
            select(Source).where(Source.is_active.is_(True), Source.source_type == "web_scraper")
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
def scrape_source_task(source_name: str) -> dict:
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

    # Create sync log entry
    sync_log = SyncLog(
        source_id=source.id,
        action="scrape",
        status="started",
    )
    session.add(sync_log)
    session.commit()

    try:
        # Run the async scraper from sync context
        scraper_cls = SCRAPER_REGISTRY[source.name]
        scraper = scraper_cls()
        scraped_events = asyncio.run(scraper.scrape())

        # Get city for deduplication
        city = session.execute(
            select(City).where(City.slug == scraper.city_slug)
        ).scalar_one_or_none()

        if city is None:
            raise RuntimeError(f"City not found for slug: {scraper.city_slug}")

        # Run dedup & store asynchronously
        from app.services.deduplicator import deduplicate_and_store
        from app.db.session import async_session

        async def _dedup():
            async with async_session() as db:
                return await deduplicate_and_store(
                    db, scraped_events, source.id, city.id
                )

        counts = asyncio.run(_dedup())

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
