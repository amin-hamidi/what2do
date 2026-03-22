"""
Scraper for dallasobserver.com — structured event listings with
date, time, venue, and price information.
"""

from __future__ import annotations

import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.services.scrapers.base import BaseScraper, ScrapedEvent

logger = logging.getLogger("what2do.scraper.dallas_observer")

BASE_URL = "https://www.dallasobserver.com"

SCRAPE_URLS = [
    f"{BASE_URL}/events/",
    f"{BASE_URL}/events/music/",
    f"{BASE_URL}/events/food-and-drink/",
    f"{BASE_URL}/events/arts/",
    f"{BASE_URL}/events/community/",
]

_CATEGORY_MAP: list[tuple[list[str], str]] = [
    (["music", "concert", "dj", "live music", "band", "festival"], "concerts"),
    (["food", "drink", "restaurant", "dining", "brunch", "tasting", "chef"], "restaurants"),
    (["nightlife", "bar", "club", "lounge", "party", "happy hour"], "nightlife"),
    (["sport", "game", "match", "run", "marathon", "fitness"], "sports"),
    (["weekend", "saturday", "sunday"], "weekend"),
]


def _classify_category(url: str, title: str, description: str = "") -> str:
    combined = f"{url} {title} {description}".lower()
    for keywords, slug in _CATEGORY_MAP:
        if any(kw in combined for kw in keywords):
            return slug
    return "activities"


def _extract_price(text: str) -> tuple[str | None, float | None, float | None]:
    """Extract price info from text. Returns (price_level, price_min, price_max)."""
    if not text:
        return None, None, None

    lower = text.lower().strip()
    if "free" in lower:
        return "free", 0.0, 0.0

    prices = re.findall(r"\$(\d+(?:\.\d{2})?)", text)
    if prices:
        amounts = [float(p) for p in prices]
        price_min = min(amounts)
        price_max = max(amounts)
        if price_max <= 15:
            level = "$"
        elif price_max <= 40:
            level = "$$"
        elif price_max <= 100:
            level = "$$$"
        else:
            level = "$$$$"
        return level, price_min, price_max

    return None, None, None


class DallasObserverScraper(BaseScraper):
    """Scraper for Dallas Observer event listings."""

    def __init__(self) -> None:
        super().__init__(source_name="dallas_observer", city_slug="dallas")

    async def scrape(self) -> list[ScrapedEvent]:
        events: list[ScrapedEvent] = []
        seen_urls: set[str] = set()

        for page_url in SCRAPE_URLS:
            try:
                html = await self._get_html(page_url)
                page_events = self._parse_listing_page(html, page_url)
                for ev in page_events:
                    if ev.source_url not in seen_urls:
                        seen_urls.add(ev.source_url)
                        events.append(ev)
            except Exception:
                self.logger.exception("Failed to scrape %s", page_url)

        self.logger.info("Scraped %d unique events from Dallas Observer", len(events))
        return events

    def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedEvent]:
        soup = BeautifulSoup(html, "lxml")
        events: list[ScrapedEvent] = []

        # Dallas Observer uses various card layouts for events
        selectors = [
            ".eventCard",
            ".event-card",
            '[class*="EventCard"]',
            ".searchResult",
            "article.event",
            ".listing-item",
            ".event-listing",
        ]

        cards: list[Tag] = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                break

        if not cards:
            cards = soup.select("div.card, article, .item")

        for card in cards:
            event = self._parse_card(card, page_url)
            if event:
                events.append(event)

        return events

    def _parse_card(self, card: Tag, page_url: str) -> ScrapedEvent | None:
        # Title + link
        title_tag = card.select_one(
            "h2 a, h3 a, .title a, .event-title a, [class*='title'] a, a.title"
        )
        if not title_tag:
            title_tag = card.select_one("a[href*='/events/']")
        if not title_tag:
            return None

        title = title_tag.get_text(strip=True)
        if not title:
            return None

        href = title_tag.get("href", "")
        source_url = urljoin(BASE_URL, str(href)) if href else page_url

        # Image
        image_url: str | None = None
        img = card.select_one("img")
        if img:
            image_url = str(
                img.get("data-src") or img.get("data-lazy-src") or img.get("src") or ""
            )
            if image_url and not image_url.startswith("http"):
                image_url = urljoin(BASE_URL, image_url)

        # Description
        description: str | None = None
        desc_tag = card.select_one(
            ".description, .excerpt, .summary, .event-description, p"
        )
        if desc_tag:
            description = desc_tag.get_text(strip=True)[:1000] or None

        # Date/time
        starts_at = None
        date_tag = card.select_one(
            "time, .date, .event-date, .when, [class*='date'], [class*='time']"
        )
        if date_tag:
            dt_attr = date_tag.get("datetime", "")
            date_text = str(dt_attr) if dt_attr else date_tag.get_text(strip=True)
            starts_at = self._parse_date(date_text)

        # Venue
        venue_name: str | None = None
        venue_tag = card.select_one(
            ".venue, .location, .event-venue, [class*='venue'], [class*='location']"
        )
        if venue_tag:
            venue_name = venue_tag.get_text(strip=True) or None

        # Price
        price_text = ""
        price_tag = card.select_one(
            ".price, .cost, .event-price, [class*='price'], [class*='cost']"
        )
        if price_tag:
            price_text = price_tag.get_text(strip=True)
        price_level, price_min, price_max = _extract_price(price_text)

        # Category
        category_slug = _classify_category(
            source_url, title, description or ""
        )

        return ScrapedEvent(
            title=title,
            source_url=source_url,
            description=description,
            image_url=image_url,
            starts_at=starts_at,
            venue_name=venue_name,
            category_slug=category_slug,
            price_level=price_level,
            price_min=price_min,
            price_max=price_max,
        )
