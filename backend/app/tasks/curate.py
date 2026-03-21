"""
Celery task for AI-powered daily event curation.
"""

import logging

from app.worker import celery_app

logger = logging.getLogger("what2do.worker")


@celery_app.task(name="curate_daily_picks")
def curate_daily_picks_task() -> dict:
    """
    Generate daily curated picks using Claude.

    TODO: Implement AI curation pipeline:
      1. Query active events for today/tomorrow
      2. Send event data to Claude for ranking and description generation
      3. Store AIPick entries with AI-generated copy
      4. Invalidate frontend cache
    """
    logger.info("curate_daily_picks_task called — not yet implemented")
    return {"status": "not_implemented"}
