"""
Celery worker for background tasks (scraping, AI curation, cleanup).
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

# --- File-based logging setup ---
LOG_DIR = os.environ.get("LOG_DIR", "/app/logs")
os.makedirs(LOG_DIR, exist_ok=True)

logger = logging.getLogger("what2do.worker")
logger.setLevel(logging.DEBUG)

file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "worker.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(file_handler)

error_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "worker-errors.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(error_handler)

# Scraper-specific log
scrape_logger = logging.getLogger("what2do.scraper")
scrape_logger.setLevel(logging.DEBUG)
scrape_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "scraper.log"),
    maxBytes=10 * 1024 * 1024,
    backupCount=5,
)
scrape_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
scrape_logger.addHandler(scrape_handler)

# --- Celery setup ---
celery_app = Celery(
    "what2do",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Chicago",
    enable_utc=True,
    task_track_started=True,
    result_expires=3600,
)

# --- Beat schedule ---
celery_app.conf.beat_schedule = {
    "scrape-all-sources": {
        "task": "scrape_all",
        "schedule": crontab(minute=0, hour="*/4"),
    },
    "daily-curate": {
        "task": "curate_daily_picks",
        "schedule": crontab(minute=0, hour=5),  # 5am CST
    },
    "cleanup-expired": {
        "task": "cleanup_expired",
        "schedule": crontab(minute=0, hour=2),  # 2am CST
    },
}


def get_sync_engine():
    """Create a sync SQLAlchemy engine for Celery tasks."""
    from sqlalchemy import create_engine

    return create_engine(settings.SYNC_DATABASE_URL)


# Import tasks so Celery discovers them
from app.tasks import scrape, curate, cleanup  # noqa: F401, E402
