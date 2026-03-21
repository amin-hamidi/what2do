"""
Deduplication service: matches scraped events against existing DB records
by content hash, creates or updates as needed.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.category import Category
from app.db.models.event import Event
from app.db.models.venue import Venue
from app.services.scrapers.base import ScrapedEvent
from app.utils.text import compute_content_hash, slugify

logger = logging.getLogger("what2do.deduplicator")


async def deduplicate_and_store(
    db: AsyncSession,
    scraped_events: list[ScrapedEvent],
    source_id: uuid.UUID,
    city_id: uuid.UUID,
) -> dict[str, int]:
    """
    Process scraped events: deduplicate against existing records and persist.

    Returns a dict with counts: found, created, updated, deduplicated.
    """
    counts = {"found": len(scraped_events), "created": 0, "updated": 0, "deduplicated": 0}

    # Pre-fetch category slugs for fast lookup
    result = await db.execute(select(Category))
    categories = {cat.slug: cat.id for cat in result.scalars().all()}

    # Default category fallback
    default_category_id = categories.get("activities")

    for scraped in scraped_events:
        try:
            content_hash = compute_content_hash(
                scraped.title, scraped.starts_at, scraped.venue_name
            )

            # Check for existing event by content hash
            existing = await db.execute(
                select(Event).where(Event.content_hash == content_hash)
            )
            existing_event = existing.scalar_one_or_none()

            if existing_event is not None:
                # Update scraped_at and merge any new fields
                existing_event.scraped_at = datetime.now(timezone.utc)

                if scraped.description and not existing_event.description:
                    existing_event.description = scraped.description
                if scraped.image_url and not existing_event.image_url:
                    existing_event.image_url = scraped.image_url
                if scraped.starts_at and not existing_event.starts_at:
                    existing_event.starts_at = scraped.starts_at
                if scraped.ends_at and not existing_event.ends_at:
                    existing_event.ends_at = scraped.ends_at
                if scraped.neighborhood and not existing_event.neighborhood:
                    existing_event.neighborhood = scraped.neighborhood
                if scraped.price_level and not existing_event.price_level:
                    existing_event.price_level = scraped.price_level
                if scraped.genre and not existing_event.genre:
                    existing_event.genre = scraped.genre

                counts["deduplicated"] += 1
                continue

            # --- Resolve venue ---
            venue_id = await _resolve_venue(db, scraped, city_id)

            # --- Resolve category ---
            category_id = categories.get(scraped.category_slug or "") or default_category_id
            if category_id is None:
                logger.warning(
                    "No category found for slug %r and no default; skipping %r",
                    scraped.category_slug,
                    scraped.title,
                )
                continue

            # --- Create new event ---
            slug = slugify(scraped.title)
            tags_str = ",".join(scraped.tags) if scraped.tags else None

            event = Event(
                city_id=city_id,
                category_id=category_id,
                venue_id=venue_id,
                source_id=source_id,
                title=scraped.title,
                slug=slug,
                description=scraped.description,
                image_url=scraped.image_url,
                source_url=scraped.source_url,
                starts_at=scraped.starts_at,
                ends_at=scraped.ends_at,
                is_all_day=scraped.is_all_day,
                tags=tags_str,
                price_level=scraped.price_level,
                price_min=scraped.price_min,
                price_max=scraped.price_max,
                genre=scraped.genre,
                cuisine_type=scraped.cuisine_type,
                neighborhood=scraped.neighborhood,
                content_hash=content_hash,
                external_id=scraped.external_id,
            )
            db.add(event)
            counts["created"] += 1

        except Exception:
            logger.exception("Error processing scraped event: %r", scraped.title)

    await db.commit()
    logger.info(
        "Dedup results: found=%d created=%d updated=%d deduplicated=%d",
        counts["found"],
        counts["created"],
        counts["updated"],
        counts["deduplicated"],
    )
    return counts


async def _resolve_venue(
    db: AsyncSession,
    scraped: ScrapedEvent,
    city_id: uuid.UUID,
) -> uuid.UUID | None:
    """Look up or create a Venue from scraped data. Returns venue ID or None."""
    if not scraped.venue_name:
        return None

    venue_slug = slugify(scraped.venue_name)

    result = await db.execute(
        select(Venue).where(Venue.city_id == city_id, Venue.slug == venue_slug)
    )
    venue = result.scalar_one_or_none()

    if venue is not None:
        # Merge address if we have new data
        if scraped.venue_address and not venue.address:
            venue.address = scraped.venue_address
        return venue.id

    venue = Venue(
        city_id=city_id,
        name=scraped.venue_name,
        slug=venue_slug,
        address=scraped.venue_address,
        neighborhood=scraped.neighborhood,
    )
    db.add(venue)
    await db.flush()
    return venue.id
