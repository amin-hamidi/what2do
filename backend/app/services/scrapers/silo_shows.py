"""
Scraper for siloshows.com — live music and concert listings in Dallas.
All events from this source map to the 'concerts' category.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.services.scrapers.base import BaseScraper, ScrapedEvent

logger = logging.getLogger("what2do.scraper.silo_shows")

BASE_URL = "https://www.siloshows.com"

SCRAPE_URLS = [
    BASE_URL,
    f"{BASE_URL}/events",
    f"{BASE_URL}/shows",
]


class SiloShowsScraper(BaseScraper):
    """Scraper for Silo Shows concert/music listings."""

    def __init__(self) -> None:
        super().__init__(source_name="silo_shows", city_slug="dallas")

    async def scrape(self) -> list[ScrapedEvent]:
        events: list[ScrapedEvent] = []
        seen_urls: set[str] = set()

        for page_url in SCRAPE_URLS:
            try:
                html = await self._get_html(page_url)
                page_events = self._parse_page(html, page_url)
                for ev in page_events:
                    if ev.source_url not in seen_urls:
                        seen_urls.add(ev.source_url)
                        events.append(ev)
            except Exception:
                self.logger.exception("Failed to scrape %s", page_url)

        self.logger.info("Scraped %d unique events from Silo Shows", len(events))
        return events

    def _parse_page(self, html: str, page_url: str) -> list[ScrapedEvent]:
        soup = BeautifulSoup(html, "lxml")
        events: list[ScrapedEvent] = []

        # Try various selectors for event cards
        selectors = [
            ".event-card",
            ".show-card",
            ".event-item",
            ".show-item",
            '[class*="event"]',
            ".listing",
            "article",
            ".card",
        ]

        cards: list[Tag] = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                break

        # Fallback: look for any links that point to event-like pages
        if not cards:
            cards = [
                tag.parent
                for tag in soup.select("a[href*='/event'], a[href*='/show']")
                if tag.parent is not None
            ]

        for card in cards:
            event = self._parse_card(card, page_url)
            if event:
                events.append(event)

        return events

    def _parse_card(self, card: Tag, page_url: str) -> ScrapedEvent | None:
        # Title + link
        title_tag = card.select_one("h2 a, h3 a, h4 a, .title a, a")
        if not title_tag:
            return None

        title = title_tag.get_text(strip=True)
        if not title or len(title) < 3:
            return None

        href = title_tag.get("href", "")
        source_url = urljoin(BASE_URL, str(href)) if href else page_url

        # Image
        image_url: str | None = None
        img = card.select_one("img")
        if img:
            image_url = str(
                img.get("data-src") or img.get("src") or ""
            )
            if image_url and not image_url.startswith("http"):
                image_url = urljoin(BASE_URL, image_url)

        # Description
        description: str | None = None
        desc_tag = card.select_one("p, .description, .details")
        if desc_tag:
            text = desc_tag.get_text(strip=True)
            if text and text != title:
                description = text[:1000]

        # Date
        starts_at = None
        date_tag = card.select_one(
            "time, .date, [class*='date'], [class*='when'], .event-date"
        )
        if date_tag:
            dt_attr = date_tag.get("datetime", "")
            date_text = str(dt_attr) if dt_attr else date_tag.get_text(strip=True)
            starts_at = self._parse_date(date_text)

        # Venue
        venue_name: str | None = None
        venue_tag = card.select_one(
            ".venue, .location, [class*='venue'], [class*='location']"
        )
        if venue_tag:
            venue_name = venue_tag.get_text(strip=True) or None

        # Price
        price_level: str | None = None
        price_min: float | None = None
        price_max: float | None = None
        price_tag = card.select_one(".price, .cost, [class*='price'], [class*='ticket']")
        if price_tag:
            price_text = price_tag.get_text(strip=True).lower()
            if "free" in price_text:
                price_level, price_min, price_max = "free", 0.0, 0.0
            else:
                amounts = re.findall(r"\$(\d+(?:\.\d{2})?)", price_text)
                if amounts:
                    vals = [float(a) for a in amounts]
                    price_min, price_max = min(vals), max(vals)
                    price_level = "$" if price_max <= 25 else "$$" if price_max <= 60 else "$$$"

        # Genre from tags or text
        genre: str | None = None
        genre_tag = card.select_one(".genre, .tag, [class*='genre']")
        if genre_tag:
            genre = genre_tag.get_text(strip=True) or None

        return ScrapedEvent(
            title=title,
            source_url=source_url,
            description=description,
            image_url=image_url,
            starts_at=starts_at,
            venue_name=venue_name,
            category_slug="concerts",
            price_level=price_level,
            price_min=price_min,
            price_max=price_max,
            genre=genre,
            tags=["live-music"],
        )
