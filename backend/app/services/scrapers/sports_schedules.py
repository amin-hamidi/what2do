"""
Scraper for Dallas sports team schedules — Mavericks, Cowboys, Stars, Rangers, FC Dallas.
Scrapes official team schedule pages for upcoming home/away games.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup, Tag

from app.services.scrapers.base import BaseScraper, ScrapedEvent

logger = logging.getLogger("what2do.scraper.sports_schedules")

CST = ZoneInfo("America/Chicago")

# Team configs: name, league, schedule URL, venue name for home games
TEAMS = [
    {
        "name": "Dallas Mavericks",
        "short_name": "Mavericks",
        "league": "NBA",
        "schedule_url": "https://www.nba.com/mavericks/schedule",
        "venue": "American Airlines Center",
        "tags": ["nba", "basketball", "mavericks"],
    },
    {
        "name": "Dallas Cowboys",
        "short_name": "Cowboys",
        "league": "NFL",
        "schedule_url": "https://www.dallascowboys.com/schedule/",
        "venue": "AT&T Stadium",
        "tags": ["nfl", "football", "cowboys"],
    },
    {
        "name": "Dallas Stars",
        "short_name": "Stars",
        "league": "NHL",
        "schedule_url": "https://www.nhl.com/stars/schedule",
        "venue": "American Airlines Center",
        "tags": ["nhl", "hockey", "stars"],
    },
    {
        "name": "Texas Rangers",
        "short_name": "Rangers",
        "league": "MLB",
        "schedule_url": "https://www.mlb.com/rangers/schedule",
        "venue": "Globe Life Field",
        "tags": ["mlb", "baseball", "rangers"],
    },
    {
        "name": "FC Dallas",
        "short_name": "FC Dallas",
        "league": "MLS",
        "schedule_url": "https://www.fcdallas.com/schedule/",
        "venue": "Toyota Stadium",
        "tags": ["mls", "soccer", "fcdallas"],
    },
]


class SportsSchedulesScraper(BaseScraper):
    """Scraper for Dallas sports team schedules."""

    def __init__(self) -> None:
        super().__init__(source_name="sports_schedules", city_slug="dallas")

    async def scrape(self) -> list[ScrapedEvent]:
        events: list[ScrapedEvent] = []
        seen: set[str] = set()

        for team in TEAMS:
            try:
                team_events = await self._scrape_team(team)
                for ev in team_events:
                    key = f"{ev.title}:{ev.starts_at}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            except Exception:
                self.logger.exception(
                    "Failed to scrape schedule for %s", team["name"]
                )

        self.logger.info("Scraped %d sports events total", len(events))
        return events

    async def _scrape_team(self, team: dict) -> list[ScrapedEvent]:
        """Scrape a single team's schedule page."""
        try:
            html = await self._get_html(team["schedule_url"])
        except Exception:
            self.logger.warning(
                "Could not fetch schedule page for %s", team["name"]
            )
            return []

        soup = BeautifulSoup(html, "lxml")
        events: list[ScrapedEvent] = []

        # Generic approach: look for schedule rows/cards
        game_selectors = [
            ".schedule__row",
            ".schedule-row",
            ".game-card",
            ".game-row",
            "tr.schedule-game",
            '[class*="ScheduleGame"]',
            '[class*="schedule-game"]',
            '[class*="GameCard"]',
            ".nfl-o-matchup-cards__item",
            "li[class*='game']",
        ]

        rows: list[Tag] = []
        for selector in game_selectors:
            rows = soup.select(selector)
            if rows:
                break

        # Fallback: try table rows
        if not rows:
            rows = soup.select("table tbody tr")

        for row in rows:
            event = self._parse_game_row(row, team)
            if event:
                events.append(event)

        # If no structured data found, try to extract from JSON-LD
        if not events:
            events = self._parse_json_ld(soup, team)

        return events

    def _parse_game_row(self, row: Tag, team: dict) -> ScrapedEvent | None:
        """Parse a single game row from a schedule table/list."""
        text = row.get_text(" ", strip=True)
        if not text or len(text) < 5:
            return None

        # Try to find opponent
        opponent = self._extract_opponent(row, team)

        # Try to find date
        starts_at = self._extract_game_date(row)

        # Try to find if home/away
        is_home = self._is_home_game(row, text)

        # Build title
        if opponent:
            if is_home:
                title = f"{team['short_name']} vs {opponent}"
            else:
                title = f"{team['short_name']} @ {opponent}"
        else:
            # Can't determine opponent, skip
            return None

        # Source URL: link in the row or fallback to schedule page
        link = row.select_one("a[href]")
        source_url = (
            urljoin(team["schedule_url"], str(link["href"]))
            if link and link.get("href")
            else team["schedule_url"]
        )

        venue_name = team["venue"] if is_home else None

        return ScrapedEvent(
            title=title,
            source_url=source_url,
            description=f"{team['league']} - {title}",
            starts_at=starts_at,
            venue_name=venue_name,
            category_slug="sports",
            tags=team["tags"],
            genre=team["league"],
        )

    def _extract_opponent(self, row: Tag, team: dict) -> str | None:
        """Try to extract opponent name from a game row."""
        # Look for opponent-specific elements
        opp_tag = row.select_one(
            ".opponent, .team-name, [class*='opponent'], [class*='team']"
        )
        if opp_tag:
            name = opp_tag.get_text(strip=True)
            if name and name != team["short_name"] and name != team["name"]:
                return name

        # Look for "vs" or "@" patterns in text
        text = row.get_text(" ", strip=True)
        vs_match = re.search(
            r"(?:vs\.?|versus)\s+(.+?)(?:\s*\d|\s*$|\s*[|])", text, re.IGNORECASE
        )
        if vs_match:
            return vs_match.group(1).strip()

        at_match = re.search(
            r"(?:@|at)\s+(.+?)(?:\s*\d|\s*$|\s*[|])", text, re.IGNORECASE
        )
        if at_match:
            return at_match.group(1).strip()

        return None

    def _extract_game_date(self, row: Tag) -> datetime | None:
        """Extract game date/time from a row."""
        # Check for time/datetime elements
        time_tag = row.select_one("time, [datetime]")
        if time_tag:
            dt_attr = time_tag.get("datetime", "")
            if dt_attr:
                parsed = self._parse_date(str(dt_attr))
                if parsed:
                    return parsed
            text = time_tag.get_text(strip=True)
            if text:
                parsed = self._parse_date(text)
                if parsed:
                    return parsed

        # Look for date-like elements
        date_tag = row.select_one(
            ".date, [class*='date'], [class*='Date'], .game-date"
        )
        if date_tag:
            text = date_tag.get_text(strip=True)
            parsed = self._parse_date(text)
            if parsed:
                return parsed

        return None

    @staticmethod
    def _is_home_game(row: Tag, text: str) -> bool:
        """Determine if this is a home game."""
        # Check for explicit home indicators
        home_tag = row.select_one("[class*='home'], .home")
        if home_tag:
            return True

        lower = text.lower()
        if " vs " in lower or " vs. " in lower:
            return True
        if " @ " in lower or " at " in lower:
            return False

        # Default to home
        return True

    def _parse_json_ld(self, soup: BeautifulSoup, team: dict) -> list[ScrapedEvent]:
        """Try to extract events from JSON-LD structured data."""
        import json

        events: list[ScrapedEvent] = []

        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "")
                items = data if isinstance(data, list) else [data]

                for item in items:
                    if item.get("@type") not in ("SportsEvent", "Event"):
                        continue

                    name = item.get("name", "")
                    if not name:
                        continue

                    start = item.get("startDate")
                    starts_at = self._parse_date(start) if start else None

                    location = item.get("location", {})
                    venue_name = location.get("name") if isinstance(location, dict) else None

                    url = item.get("url", team["schedule_url"])

                    events.append(ScrapedEvent(
                        title=name,
                        source_url=url,
                        description=item.get("description", f"{team['league']} game"),
                        starts_at=starts_at,
                        venue_name=venue_name or team["venue"],
                        category_slug="sports",
                        tags=team["tags"],
                        genre=team["league"],
                    ))
            except (json.JSONDecodeError, TypeError):
                continue

        return events
