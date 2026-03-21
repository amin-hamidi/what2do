"""
Scraper for dallasites101.com — a popular Dallas lifestyle blog covering
restaurants, events, activities, and nightlife.
"""

from __future__ import annotations

import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from app.services.scrapers.base import BaseScraper, ScrapedEvent

logger = logging.getLogger("what2do.scraper.dallasites101")

BASE_URL = "https://www.dallasites101.com"

# Pages to scrape for different content types
SCRAPE_URLS = [
    f"{BASE_URL}/things-to-do-in-dallas-this-week/",
    f"{BASE_URL}/things-to-do-in-dallas-this-weekend/",
    f"{BASE_URL}/category/restaurants/",
    f"{BASE_URL}/category/things-to-do/",
]

# URL path / keyword -> category slug mapping
_CATEGORY_MAP: list[tuple[list[str], str]] = [
    (["restaurant", "food", "dining", "brunch", "eat", "cuisine", "chef"], "restaurants"),
    (["nightlife", "bar", "club", "lounge", "cocktail", "rooftop"], "nightlife"),
    (["concert", "music", "live-music", "festival"], "concerts"),
    (["sport", "game", "match", "stadium"], "sports"),
    (["weekend", "saturday", "sunday"], "weekend"),
]


def _classify_category(url: str, title: str) -> str:
    """Determine category slug from the article URL and title."""
    combined = f"{url} {title}".lower()
    for keywords, slug in _CATEGORY_MAP:
        if any(kw in combined for kw in keywords):
            return slug
    return "activities"


class Dallasites101Scraper(BaseScraper):
    """Concrete scraper for dallasites101.com."""

    def __init__(self) -> None:
        super().__init__(source_name="dallasites101", city_slug="dallas")

    async def scrape(self) -> list[ScrapedEvent]:
        """Fetch and parse event/article listings from dallasites101.com."""
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

        self.logger.info("Scraped %d unique events from dallasites101", len(events))
        return events

    def _parse_listing_page(self, html: str, page_url: str) -> list[ScrapedEvent]:
        """Parse a listing page and extract article entries."""
        soup = BeautifulSoup(html, "lxml")
        events: list[ScrapedEvent] = []

        # TODO: Selectors may need adjustment after inspecting the live site.
        # dallasites101 is a WordPress site; these target common WP article patterns.
        article_selectors = [
            "article.post",
            "article.type-post",
            ".entry-card",
            ".post-card",
            ".wp-block-post",
        ]

        articles: list[Tag] = []
        for selector in article_selectors:
            articles = soup.select(selector)
            if articles:
                break

        if not articles:
            # Fallback: grab all <article> tags
            articles = soup.find_all("article")

        for article in articles:
            event = self._parse_article(article, page_url)
            if event:
                events.append(event)

        return events

    def _parse_article(self, article: Tag, page_url: str) -> ScrapedEvent | None:
        """Extract event data from a single article element."""
        # --- Title and link ---
        # TODO: Adjust heading selector based on live site structure
        title_tag = article.select_one(
            "h2.entry-title a, h2 a, h3.entry-title a, h3 a, .post-title a"
        )
        if not title_tag:
            return None

        title = title_tag.get_text(strip=True)
        if not title:
            return None

        href = title_tag.get("href", "")
        source_url = urljoin(BASE_URL, str(href)) if href else page_url

        # --- Image ---
        image_url: str | None = None
        img_tag = article.select_one(
            "img.wp-post-image, .post-thumbnail img, .entry-image img, img"
        )
        if img_tag:
            # Prefer data-src (lazy loading) over src
            image_url = str(
                img_tag.get("data-src") or img_tag.get("data-lazy-src") or img_tag.get("src") or ""
            )
            if image_url and not image_url.startswith("http"):
                image_url = urljoin(BASE_URL, image_url)

        # --- Description / excerpt ---
        description: str | None = None
        excerpt_tag = article.select_one(
            ".entry-summary, .entry-excerpt, .post-excerpt, .entry-content p"
        )
        if excerpt_tag:
            description = excerpt_tag.get_text(strip=True)[:1000] or None

        # --- Date ---
        starts_at = None
        date_tag = article.select_one("time, .entry-date, .post-date, .published")
        if date_tag:
            datetime_attr = date_tag.get("datetime", "")
            date_text = str(datetime_attr) if datetime_attr else date_tag.get_text(strip=True)
            starts_at = self._parse_date(date_text)

        # --- Category classification ---
        category_slug = _classify_category(source_url, title)

        # --- Tags from article classes ---
        tags: list[str] = []
        css_classes = article.get("class", [])
        if isinstance(css_classes, list):
            for cls in css_classes:
                if cls.startswith("tag-"):
                    tags.append(cls.removeprefix("tag-"))
                elif cls.startswith("category-"):
                    tags.append(cls.removeprefix("category-"))

        return ScrapedEvent(
            title=title,
            source_url=source_url,
            description=description,
            image_url=image_url,
            starts_at=starts_at,
            category_slug=category_slug,
            tags=tags,
            raw_data={"page_url": page_url},
        )
