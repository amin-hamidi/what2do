"""
Abstract base scraper and shared data structures for all event scrapers.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

import httpx
from zoneinfo import ZoneInfo

from app.core.config import get_settings

logger = logging.getLogger("what2do.scraper")

CST = ZoneInfo("America/Chicago")

# Date formats commonly found on event listing sites
_DATE_FORMATS = [
    "%B %d, %Y",            # January 15, 2026
    "%b %d, %Y",            # Jan 15, 2026
    "%m/%d/%Y",             # 01/15/2026
    "%m-%d-%Y",             # 01-15-2026
    "%Y-%m-%d",             # 2026-01-15
    "%Y-%m-%dT%H:%M:%S",   # 2026-01-15T19:00:00
    "%B %d, %Y %I:%M %p",  # January 15, 2026 7:00 PM
    "%b %d, %Y %I:%M %p",  # Jan 15, 2026 7:00 PM
    "%m/%d/%Y %I:%M %p",   # 01/15/2026 7:00 PM
    "%A, %B %d, %Y",       # Wednesday, January 15, 2026
    "%A, %B %d",            # Wednesday, January 15
    "%B %d",                # January 15
]

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


@dataclass
class ScrapedEvent:
    """Normalized event data returned by any scraper."""

    title: str
    source_url: str
    description: str | None = None
    image_url: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_all_day: bool = False
    venue_name: str | None = None
    venue_address: str | None = None
    neighborhood: str | None = None
    category_slug: str | None = None
    tags: list[str] = field(default_factory=list)
    price_level: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    genre: str | None = None
    cuisine_type: str | None = None
    external_id: str | None = None
    raw_data: dict | None = None


class BaseScraper(ABC):
    """Abstract base class for all event scrapers."""

    def __init__(self, source_name: str, city_slug: str = "dallas") -> None:
        self.source_name = source_name
        self.city_slug = city_slug
        self.settings = get_settings()
        self.logger = logging.getLogger(f"what2do.scraper.{source_name}")

    @abstractmethod
    async def scrape(self) -> list[ScrapedEvent]:
        """Fetch and parse events from the source. Must be implemented by subclasses."""
        ...

    async def _get_html(self, url: str) -> str:
        """Fetch HTML content from a URL with timeout, user-agent, and retries."""
        timeout = httpx.Timeout(self.settings.SCRAPE_TIMEOUT_S, connect=10.0)
        retries = self.settings.SCRAPE_MAX_RETRIES

        last_exc: Exception | None = None
        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=timeout,
                    headers={"User-Agent": USER_AGENT},
                    follow_redirects=True,
                ) as client:
                    resp = await client.get(url)
                    resp.raise_for_status()
                    return resp.text
            except (httpx.HTTPStatusError, httpx.RequestError) as exc:
                last_exc = exc
                self.logger.warning(
                    "Attempt %d/%d failed for %s: %s", attempt, retries, url, exc
                )

        raise RuntimeError(
            f"Failed to fetch {url} after {retries} attempts"
        ) from last_exc

    @staticmethod
    def _parse_date(raw: str) -> datetime | None:
        """Try multiple date formats and return a tz-aware datetime (America/Chicago)."""
        cleaned = raw.strip()
        if not cleaned:
            return None

        for fmt in _DATE_FORMATS:
            try:
                dt = datetime.strptime(cleaned, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=CST)
                return dt
            except ValueError:
                continue

        logger.debug("Could not parse date string: %r", raw)
        return None
