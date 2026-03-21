"""
Database seed script — populates initial reference data.

Run with: python -m app.db.seed
"""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.category import Category
from app.db.models.city import City
from app.db.models.source import Source
from app.db.models.sports_team import SportsTeam
from app.db.models.venue import Venue
from app.db.session import async_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("what2do.seed")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _get_or_create(db: AsyncSession, model, defaults: dict, **lookup):
    """Return existing row or create a new one. Idempotent."""
    stmt = select(model)
    for attr, value in lookup.items():
        stmt = stmt.where(getattr(model, attr) == value)
    result = await db.execute(stmt)
    instance = result.scalar_one_or_none()
    if instance is not None:
        return instance, False

    instance = model(**lookup, **defaults)
    db.add(instance)
    await db.flush()
    return instance, True


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

CATEGORIES = [
    {"slug": "concerts", "name": "Music", "sort_order": 1, "icon": "music"},
    {"slug": "restaurants", "name": "Restaurants", "sort_order": 2, "icon": "utensils-crossed"},
    {"slug": "activities", "name": "Activities & Events", "sort_order": 3, "icon": "calendar-days"},
    {"slug": "sports", "name": "Sports", "sort_order": 4, "icon": "trophy"},
    {"slug": "nightlife", "name": "Nightlife", "sort_order": 5, "icon": "wine"},
    {"slug": "weekend", "name": "Weekend Planner", "sort_order": 6, "icon": "sparkles"},
]

SOURCES = [
    {
        "name": "dallasites101",
        "source_type": "web_scraper",
        "base_url": "https://www.dallasites101.com/",
        "scraper_class": "Dallasites101Scraper",
    },
    {
        "name": "dallas_observer",
        "source_type": "web_scraper",
        "base_url": "https://www.dallasobserver.com/",
        "scraper_class": None,
    },
    {
        "name": "silo_shows",
        "source_type": "web_scraper",
        "base_url": "https://www.siloshows.com/",
        "scraper_class": None,
    },
    {
        "name": "visit_dallas",
        "source_type": "web_scraper",
        "base_url": "https://www.visitdallas.com/",
        "scraper_class": None,
    },
    {
        "name": "x_social",
        "source_type": "x_social",
        "base_url": None,
        "scraper_class": None,
    },
]

VENUES = [
    {
        "name": "American Airlines Center",
        "slug": "american-airlines-center",
        "address": "2500 Victory Ave, Dallas, TX 75219",
        "neighborhood": "Victory Park",
        "venue_type": "arena",
        "latitude": 32.7906,
        "longitude": -96.8103,
    },
    {
        "name": "AT&T Stadium",
        "slug": "att-stadium",
        "address": "1 AT&T Way, Arlington, TX 76011",
        "neighborhood": "Arlington",
        "venue_type": "stadium",
        "latitude": 32.7473,
        "longitude": -97.0945,
    },
    {
        "name": "Globe Life Field",
        "slug": "globe-life-field",
        "address": "734 Stadium Dr, Arlington, TX 76011",
        "neighborhood": "Arlington",
        "venue_type": "stadium",
        "latitude": 32.7512,
        "longitude": -97.0832,
    },
    {
        "name": "Toyota Stadium",
        "slug": "toyota-stadium",
        "address": "9200 World Cup Way, Frisco, TX 75033",
        "neighborhood": "Frisco",
        "venue_type": "stadium",
        "latitude": 33.1543,
        "longitude": -96.8353,
    },
    {
        "name": "Trees",
        "slug": "trees",
        "address": "2709 Elm St, Dallas, TX 75226",
        "neighborhood": "Deep Ellum",
        "venue_type": "music_venue",
    },
    {
        "name": "The Bomb Factory",
        "slug": "the-bomb-factory",
        "address": "2713 Canton St, Dallas, TX 75226",
        "neighborhood": "Deep Ellum",
        "venue_type": "music_venue",
    },
    {
        "name": "Deep Ellum Art Co",
        "slug": "deep-ellum-art-co",
        "address": "3200 Commerce St, Dallas, TX 75226",
        "neighborhood": "Deep Ellum",
        "venue_type": "music_venue",
    },
    {
        "name": "Club Dada",
        "slug": "club-dada",
        "address": "2720 Elm St, Dallas, TX 75226",
        "neighborhood": "Deep Ellum",
        "venue_type": "music_venue",
    },
    {
        "name": "The Echo Lounge & Music Hall",
        "slug": "the-echo-lounge-music-hall",
        "address": "1323 N Stemmons Fwy, Dallas, TX 75207",
        "neighborhood": "Design District",
        "venue_type": "music_venue",
    },
]

SPORTS_TEAMS = [
    {"name": "Dallas Mavericks", "short_name": "Mavericks", "league": "NBA", "venue_slug": "american-airlines-center"},
    {"name": "Dallas Cowboys", "short_name": "Cowboys", "league": "NFL", "venue_slug": "att-stadium"},
    {"name": "Dallas Stars", "short_name": "Stars", "league": "NHL", "venue_slug": "american-airlines-center"},
    {"name": "Texas Rangers", "short_name": "Rangers", "league": "MLB", "venue_slug": "globe-life-field"},
    {"name": "FC Dallas", "short_name": "FC Dallas", "league": "MLS", "venue_slug": "toyota-stadium"},
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    """Seed the database with initial reference data."""
    async with async_session() as db:
        # --- City ---
        city, created = await _get_or_create(
            db, City,
            defaults={
                "name": "Dallas, TX",
                "state": "TX",
                "timezone": "America/Chicago",
                "latitude": 32.7767,
                "longitude": -96.7970,
            },
            slug="dallas",
        )
        logger.info("City 'dallas': %s", "created" if created else "exists")

        # --- Categories ---
        for cat_data in CATEGORIES:
            slug = cat_data.pop("slug")
            _, created = await _get_or_create(db, Category, defaults=cat_data, slug=slug)
            cat_data["slug"] = slug  # restore for idempotency on re-run
            logger.info("Category '%s': %s", slug, "created" if created else "exists")

        # --- Sources ---
        for src_data in SOURCES:
            name = src_data["name"]
            _, created = await _get_or_create(
                db, Source,
                defaults={
                    "source_type": src_data["source_type"],
                    "base_url": src_data["base_url"],
                    "scraper_class": src_data["scraper_class"],
                },
                name=name,
            )
            logger.info("Source '%s': %s", name, "created" if created else "exists")

        # --- Venues ---
        venue_map: dict[str, Venue] = {}
        for v_data in VENUES:
            slug = v_data["slug"]
            defaults = {k: v for k, v in v_data.items() if k not in ("slug",)}
            defaults["city_id"] = city.id
            venue, created = await _get_or_create(
                db, Venue,
                defaults=defaults,
                slug=slug,
                city_id=city.id,
            )
            venue_map[slug] = venue
            logger.info("Venue '%s': %s", v_data["name"], "created" if created else "exists")

        # --- Sports Teams ---
        for team_data in SPORTS_TEAMS:
            venue_slug = team_data.pop("venue_slug")
            venue = venue_map.get(venue_slug)
            defaults = {
                "short_name": team_data["short_name"],
                "league": team_data["league"],
                "city_id": city.id,
                "venue_id": venue.id if venue else None,
            }
            _, created = await _get_or_create(
                db, SportsTeam,
                defaults=defaults,
                name=team_data["name"],
            )
            team_data["venue_slug"] = venue_slug  # restore
            logger.info("Team '%s': %s", team_data["name"], "created" if created else "exists")

        await db.commit()
        logger.info("Seed complete.")


if __name__ == "__main__":
    asyncio.run(main())
