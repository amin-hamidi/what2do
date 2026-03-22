"""
X/Twitter social scraper — monitors curated Dallas accounts for event-like
posts. Adapted from the XClient in news_summary/daily_digest_xbot/x_client.py
to use async httpx.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta, timezone

import httpx

from app.services.scrapers.base import BaseScraper, ScrapedEvent

logger = logging.getLogger("what2do.scraper.x_social")

# Curated Dallas accounts to monitor for events
DALLAS_ACCOUNTS = [
    # Food & Restaurants
    "daborneats",
    "DallasFoodNerd",
    "daborneats",
    "EatDrinkDallas",
    "dfwfoodie",
    "DallasEater",
    # Events & Lifestyle
    "Dallasites101",
    "SecretDallas",
    "DallasDoList",
    "CultureMapDAL",
    "GuideLive",
    # Nightlife & Music
    "DallasObserver",
    "DeepEllumTX",
    "TreesDallas",
    "BombFactory",
    # Sports
    "dalaborstars",
    "dalaborstars",
]

# Event-like keywords that suggest a post is about an event
_EVENT_KEYWORDS = [
    "tonight", "this weekend", "this saturday", "this sunday",
    "happening now", "coming up", "don't miss", "tickets",
    "new restaurant", "now open", "grand opening", "just opened",
    "pop-up", "popup", "food truck", "brunch", "happy hour",
    "live music", "concert", "show", "festival", "market",
    "free event", "free admission", "rsvp",
    "game day", "vs.", "matchup",
]

_CATEGORY_MAP: list[tuple[list[str], str]] = [
    (["concert", "music", "live music", "dj", "show", "band", "festival"], "concerts"),
    (["restaurant", "food", "dining", "brunch", "eat", "opened", "opening", "food truck"], "restaurants"),
    (["nightlife", "bar", "club", "lounge", "cocktail", "happy hour", "party"], "nightlife"),
    (["game", "vs.", "matchup", "mavericks", "cowboys", "stars", "rangers", "fc dallas"], "sports"),
    (["weekend", "saturday", "sunday"], "weekend"),
]


def _classify_category(text: str) -> str:
    lower = text.lower()
    for keywords, slug in _CATEGORY_MAP:
        if any(kw in lower for kw in keywords):
            return slug
    return "activities"


def _is_event_like(text: str) -> bool:
    """Check if a tweet contains event-related keywords."""
    lower = text.lower()
    return any(kw in lower for kw in _EVENT_KEYWORDS)


def _extract_title(text: str) -> str:
    """Extract a concise title from tweet text."""
    # Remove URLs
    cleaned = re.sub(r"https?://\S+", "", text).strip()
    # Remove hashtags at the end
    cleaned = re.sub(r"(\s*#\w+)+$", "", cleaned).strip()
    # Take first sentence or first 120 chars
    first_sentence = re.split(r"[.!\n]", cleaned)[0].strip()
    if len(first_sentence) > 120:
        return first_sentence[:117] + "..."
    return first_sentence or cleaned[:120]


class AsyncXClient:
    """Async X API v2 client using httpx, adapted from news_summary XClient."""

    BASE = "https://api.x.com/2"

    def __init__(self, bearer_token: str, timeout_s: int = 60, max_retries: int = 2):
        self._bearer_token = bearer_token
        self._timeout = timeout_s
        self._max_retries = max_retries

    async def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.BASE}{path}"
        last_err: Exception | None = None

        for attempt in range(1, self._max_retries + 1):
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self._timeout),
                    headers={
                        "Authorization": f"Bearer {self._bearer_token}",
                        "User-Agent": "what2do-scraper/0.1",
                    },
                ) as client:
                    r = await client.get(url, params=params)
                    if not r.is_success:
                        raise RuntimeError(f"X API error {r.status_code}: {r.text}")
                    return r.json()
            except (httpx.TimeoutException, httpx.ConnectError) as e:
                last_err = e
                logger.warning(
                    "X API request to %s failed (attempt %d/%d): %s",
                    path, attempt, self._max_retries, e,
                )

        raise RuntimeError(
            f"X API request to {path} failed after {self._max_retries} attempts: {last_err}"
        )

    async def get_user_id(self, username: str) -> str:
        data = await self._get(f"/users/by/username/{username}")
        user = data.get("data") or {}
        uid = user.get("id")
        if not uid:
            raise RuntimeError(
                f"Could not resolve @{username} to a user id. Response: {data}"
            )
        return uid

    async def get_posts(
        self,
        user_id: str,
        username: str,
        start_time_utc_iso: str,
        end_time_utc_iso: str,
        max_pages: int = 5,
    ) -> list[dict]:
        all_posts: list[dict] = []
        pagination_token: str | None = None
        page = 0

        while page < max_pages:
            page += 1
            params: dict = {
                "start_time": start_time_utc_iso,
                "end_time": end_time_utc_iso,
                "max_results": 100,
                "tweet.fields": "created_at",
                "exclude": "replies,retweets",
            }
            if pagination_token:
                params["pagination_token"] = pagination_token

            data = await self._get(f"/users/{user_id}/tweets", params=params)
            items = data.get("data") or []

            for item in items:
                tid = item.get("id")
                all_posts.append({
                    "id": tid,
                    "username": username,
                    "created_at": item.get("created_at", ""),
                    "text": item.get("text", ""),
                    "url": f"https://x.com/{username}/status/{tid}" if tid else "",
                })

            meta = data.get("meta") or {}
            pagination_token = meta.get("next_token")
            if not pagination_token:
                break

        return all_posts


class XSocialScraper(BaseScraper):
    """Scraper that monitors curated Dallas X/Twitter accounts for events."""

    def __init__(self) -> None:
        super().__init__(source_name="x_social", city_slug="dallas")

    async def scrape(self) -> list[ScrapedEvent]:
        token = self.settings.X_BEARER_TOKEN
        if not token:
            self.logger.warning("X_BEARER_TOKEN not set, skipping X social scraper")
            return []

        client = AsyncXClient(bearer_token=token)
        events: list[ScrapedEvent] = []
        seen_urls: set[str] = set()

        # Look at posts from the last 24 hours
        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=24)
        start_iso = start.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Deduplicate account list
        accounts = list(dict.fromkeys(DALLAS_ACCOUNTS))

        for username in accounts:
            try:
                user_id = await client.get_user_id(username)
                posts = await client.get_posts(
                    user_id=user_id,
                    username=username,
                    start_time_utc_iso=start_iso,
                    end_time_utc_iso=end_iso,
                    max_pages=2,
                )

                for post in posts:
                    text = post.get("text", "")
                    url = post.get("url", "")

                    if not _is_event_like(text):
                        continue

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = _extract_title(text)
                    if not title:
                        continue

                    # Parse created_at
                    starts_at = None
                    created = post.get("created_at", "")
                    if created:
                        starts_at = self._parse_date(created)

                    category_slug = _classify_category(text)

                    events.append(ScrapedEvent(
                        title=title,
                        source_url=url,
                        description=text[:1000] if text else None,
                        starts_at=starts_at,
                        category_slug=category_slug,
                        external_id=post.get("id"),
                        tags=["x-social", f"@{username}"],
                        raw_data=post,
                    ))

            except Exception:
                self.logger.exception("Failed to fetch posts from @%s", username)

        self.logger.info("Scraped %d event-like posts from X", len(events))
        return events
