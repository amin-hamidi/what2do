"""
Celery task for AI-powered daily event curation.
"""

import asyncio
import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models.city import City
from app.services.ai_curator import curate_daily_picks
from app.worker import celery_app

logger = logging.getLogger("what2do.worker")


@celery_app.task(name="curate_daily_picks")
def curate_daily_picks_task(city_slug: str = "dallas") -> dict:
    """
    Generate daily curated picks using Claude.
    Runs via Celery Beat at 5am CST daily.
    """
    logger.info("Starting curate_daily_picks_task for %s", city_slug)

    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, skipping curation")
        return {"status": "skipped", "reason": "no_api_key"}

    async def _run():
        engine = create_async_engine(settings.ASYNC_DATABASE_URL)
        session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        try:
            async with session_factory() as db:
                city_result = await db.execute(
                    select(City).where(City.slug == city_slug)
                )
                city = city_result.scalar_one_or_none()
                if not city:
                    return {"status": "error", "reason": f"City '{city_slug}' not found"}

                return await curate_daily_picks(db, city.id, date.today())
        finally:
            await engine.dispose()

    result = asyncio.run(_run())
    logger.info("curate_daily_picks_task result: %s", result)
    return result
