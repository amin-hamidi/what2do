"""
Scraper for visitdallas.com — official Dallas tourism site with event listings.
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.services.scrapers.base import BaseScraper, ScrapedEvent

logger = logging.getLogger("what2do.scraper.visit_dallas")

BASE_URL = "https://www.visitdallas.com"

SCRAPE_URLS = [
    f"{BASE_URL}/events/",
    f"{BASE_URL}/things-to-do/",
    f"{BASE_URL}/things-to-do/nightlife/",
    f"{BASE_URL}/food-drink/",
]

_CATEGORY_MAP: list[tuple[list[str], str]] = [
    (["concert", "music", "live", "festival", "band", "dj"], "concerts"),
    (["restaurant", "food", "dining", "brunch", "eat", "drink", "chef", "cuisine"], "restaurants"),
    (["nightlife", "bar", "club", "lounge", "cocktail", "rooftop", "party"], "nightlife"),
    (["sport", "game", "match", "stadium", "arena"], "sports"),
    (["weekend", "saturday", "sunday"], "weekend"),
]


def _classify_category(url: str, title: str, description: str = "") -> str:
    combined = f"{url} {title} {description}".lower()
    for keywords, slug in _CATEGORY_MAP:
        if any(kw in combined for kw in keywords):
            return slug
    return "activities"


class VisitDallasScraper(BaseScraper):
    """Scraper for Visit Dallas official tourism event listings."""

    def __init__(self) -> None:
        super().__init__(source_name="visit_dallas", city_slug="dallas")

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

        self.logger.info("Scraped %d unique events from Visit Dallas", len(events))
        return events

    def _parse_page(self, html: str, page_url: str) -> list[ScrapedEvent]:
        soup = BeautifulSoup(html, "lxml")
        events: list[ScrapedEvent] = []

        selectors = [
            ".event-card",
            ".event-item",
            ".listing-card",
            ".card",
            '[class*="event"]',
            '[class*="listing"]',
            "article",
        ]

        cards: list[Tag] = []
        for selector in selectors:
            cards = soup.select(selector)
            if cards:
                break

        if not cards:
            cards = soup.find_all("article")

        for card in cards:
            event = self._parse_card(card, page_url)
            if event:
                events.append(event)

        return events

    def _parse_card(self, card: Tag, page_url: str) -> ScrapedEvent | None:
        # Title + link
        title_tag = card.select_one(
            "h2 a, h3 a, h4 a, .title a, .card-title a, a[href]"
        )
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
                img.get("data-src") or img.get("data-lazy-src") or img.get("src") or ""
            )
            if image_url and not image_url.startswith("http"):
                image_url = urljoin(BASE_URL, image_url)

        # Description
        description: str | None = None
        desc_tag = card.select_one(
            ".description, .excerpt, .summary, .card-text, p"
        )
        if desc_tag:
            text = desc_tag.get_text(strip=True)
            if text and text != title:
                description = text[:1000]

        # Date
        starts_at = None
        date_tag = card.select_one(
            "time, .date, .event-date, [class*='date']"
        )
        if date_tag:
            dt_attr = date_tag.get("datetime", "")
            date_text = str(dt_attr) if dt_attr else date_tag.get_text(strip=True)
            starts_at = self._parse_date(date_text)

        # Venue / location
        venue_name: str | None = None
        neighborhood: str | None = None
        loc_tag = card.select_one(
            ".venue, .location, [class*='venue'], [class*='location'], .address"
        )
        if loc_tag:
            loc_text = loc_tag.get_text(strip=True)
            if loc_text:
                venue_name = loc_text

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
            neighborhood=neighborhood,
            category_slug=category_slug,
        )
