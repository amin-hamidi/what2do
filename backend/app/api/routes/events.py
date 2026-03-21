from datetime import date, datetime, time, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_db
from app.db.models.category import Category
from app.db.models.city import City
from app.db.models.event import Event
from app.db.models.source import Source
from app.db.models.venue import Venue
from app.schemas.event import EventFilters, EventListResponse, EventResponse

router = APIRouter()


async def _get_city(db: AsyncSession, city_slug: str) -> City:
    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


def _event_to_response(event: Event) -> EventResponse:
    return EventResponse(
        id=event.id,
        city_id=event.city_id,
        category_id=event.category_id,
        venue_id=event.venue_id,
        source_id=event.source_id,
        title=event.title,
        slug=event.slug,
        description=event.description,
        short_description=event.short_description,
        image_url=event.image_url,
        source_url=event.source_url,
        starts_at=event.starts_at,
        ends_at=event.ends_at,
        is_all_day=event.is_all_day,
        tags=event.tags,
        price_level=event.price_level,
        price_min=event.price_min,
        price_max=event.price_max,
        genre=event.genre,
        cuisine_type=event.cuisine_type,
        neighborhood=event.neighborhood,
        status=event.status,
        content_hash=event.content_hash,
        created_at=event.created_at,
        scraped_at=event.scraped_at,
        venue_name=event.venue.name if event.venue else None,
        category_name=event.category.name if event.category else None,
        source_name=event.source.name if event.source else None,
    )


@router.get("/{city_slug}/events", response_model=EventListResponse)
async def list_events(
    city_slug: str,
    category: str | None = Query(None),
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    venue_id: str | None = Query(None),
    neighborhood: str | None = Query(None),
    genre: str | None = Query(None),
    cuisine_type: str | None = Query(None),
    price_level: str | None = Query(None),
    tags: str | None = Query(None),
    q: str | None = Query(None),
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> EventListResponse:
    city = await _get_city(db, city_slug)

    stmt = (
        select(Event)
        .where(Event.city_id == city.id, Event.status == "active")
        .outerjoin(Venue, Event.venue_id == Venue.id)
        .join(Category, Event.category_id == Category.id)
        .join(Source, Event.source_id == Source.id)
        .options(
            selectinload(Event.venue),
            selectinload(Event.category),
            selectinload(Event.source),
        )
    )

    # Apply filters
    if category:
        stmt = stmt.where(Category.slug == category)
    if date_from:
        stmt = stmt.where(
            Event.starts_at >= datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        )
    if date_to:
        stmt = stmt.where(
            Event.starts_at <= datetime.combine(date_to, time.max, tzinfo=timezone.utc)
        )
    if venue_id:
        stmt = stmt.where(Event.venue_id == UUID(venue_id))
    if neighborhood:
        stmt = stmt.where(Event.neighborhood.ilike(f"%{neighborhood}%"))
    if genre:
        stmt = stmt.where(Event.genre.ilike(f"%{genre}%"))
    if cuisine_type:
        stmt = stmt.where(Event.cuisine_type.ilike(f"%{cuisine_type}%"))
    if price_level:
        stmt = stmt.where(Event.price_level == price_level)
    if tags:
        stmt = stmt.where(Event.tags.ilike(f"%{tags}%"))
    if q:
        search = f"%{q}%"
        stmt = stmt.where(
            Event.title.ilike(search) | Event.description.ilike(search)
        )

    # Count total before pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # Cursor-based pagination: events after the given UUID, ordered by starts_at
    stmt = stmt.order_by(Event.starts_at.asc().nullslast(), Event.id.asc())
    if cursor:
        cursor_event = await db.execute(
            select(Event.starts_at).where(Event.id == UUID(cursor))
        )
        cursor_row = cursor_event.one_or_none()
        if cursor_row:
            cursor_starts_at = cursor_row[0]
            stmt = stmt.where(
                (Event.starts_at > cursor_starts_at)
                | ((Event.starts_at == cursor_starts_at) & (Event.id > UUID(cursor)))
            )

    stmt = stmt.limit(limit)
    result = await db.execute(stmt)
    events = result.scalars().unique().all()

    items = [_event_to_response(e) for e in events]
    next_cursor = str(items[-1].id) if len(items) == limit else None

    return EventListResponse(items=items, total=total, cursor=next_cursor)


@router.get("/{city_slug}/events/calendar", response_model=dict[str, list[EventResponse]])
async def events_calendar(
    city_slug: str,
    date_from: date | None = Query(None),
    date_to: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, list[EventResponse]]:
    city = await _get_city(db, city_slug)

    stmt = (
        select(Event)
        .where(Event.city_id == city.id, Event.status == "active")
        .options(
            selectinload(Event.venue),
            selectinload(Event.category),
            selectinload(Event.source),
        )
        .order_by(Event.starts_at.asc().nullslast())
    )

    if date_from:
        stmt = stmt.where(
            Event.starts_at >= datetime.combine(date_from, time.min, tzinfo=timezone.utc)
        )
    if date_to:
        stmt = stmt.where(
            Event.starts_at <= datetime.combine(date_to, time.max, tzinfo=timezone.utc)
        )

    result = await db.execute(stmt)
    events = result.scalars().unique().all()

    grouped: dict[str, list[EventResponse]] = {}
    for event in events:
        if event.starts_at:
            date_key = event.starts_at.date().isoformat()
        else:
            date_key = "undated"
        grouped.setdefault(date_key, []).append(_event_to_response(event))

    return grouped
