"""
Celery task for cleaning up expired events.
"""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import update

from app.db.models.event import Event
from app.worker import celery_app, get_sync_engine

logger = logging.getLogger("what2do.worker")


@celery_app.task(name="cleanup_expired")
def cleanup_expired_task() -> dict:
    """Mark events as expired where starts_at < now - 1 day and status is active."""
    from sqlalchemy.orm import Session

    cutoff = datetime.now(timezone.utc) - timedelta(days=1)
    engine = get_sync_engine()

    with Session(engine) as session:
        result = session.execute(
            update(Event)
            .where(
                Event.starts_at < cutoff,
                Event.status == "active",
                Event.starts_at.isnot(None),
            )
            .values(status="expired")
        )
        count = result.rowcount
        session.commit()

    logger.info("cleanup_expired_task: marked %d events as expired", count)
    return {"expired_count": count}
