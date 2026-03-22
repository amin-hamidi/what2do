from collections import defaultdict
from datetime import date, datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import cache_get, cache_set
from app.core.deps import get_db
from app.db.models.ai_pick import AIPick
from app.db.models.city import City
from app.db.models.event import Event
from app.schemas.ai_pick import AIPickResponse, DailyPicksResponse
from app.schemas.event import EventResponse

router = APIRouter()


async def _get_city(db: AsyncSession, city_slug: str) -> City:
    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")
    return city


def _pick_to_response(pick: AIPick) -> AIPickResponse:
    event = pick.event
    event_resp = None
    if event:
        event_resp = EventResponse(
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

    return AIPickResponse(
        id=pick.id,
        event_id=pick.event_id,
        pick_date=pick.pick_date,
        pick_type=pick.pick_type,
        rank=pick.rank,
        ai_blurb=pick.ai_blurb,
        event=event_resp,
    )


async def _get_picks_for_date(
    db: AsyncSession, city_id, pick_date: date
) -> DailyPicksResponse:
    stmt = (
        select(AIPick)
        .where(AIPick.city_id == city_id, AIPick.pick_date == pick_date)
        .options(
            selectinload(AIPick.event).selectinload(Event.venue),
            selectinload(AIPick.event).selectinload(Event.category),
            selectinload(AIPick.event).selectinload(Event.source),
        )
        .order_by(AIPick.rank.asc())
    )
    result = await db.execute(stmt)
    picks = result.scalars().unique().all()

    top_pick: AIPickResponse | None = None
    categories: dict[str, list[AIPickResponse]] = defaultdict(list)

    for pick in picks:
        resp = _pick_to_response(pick)
        if pick.pick_type == "top_pick" and pick.rank == 1:
            top_pick = resp
        else:
            categories[pick.pick_type].append(resp)

    return DailyPicksResponse(top_pick=top_pick, categories=dict(categories))


@router.get("/{city_slug}/picks", response_model=DailyPicksResponse)
async def todays_picks(
    city_slug: str,
    db: AsyncSession = Depends(get_db),
):
    # Use city timezone for "today" (not UTC)
    city_obj = await _get_city(db, city_slug)
    tz = ZoneInfo(city_obj.timezone if city_obj.timezone else "America/Chicago")
    today = datetime.now(tz).date()
    cache_key = f"picks:{city_slug}:{today.isoformat()}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return JSONResponse(content=cached)

    result = await _get_picks_for_date(db, city_obj.id, today)

    # Cache for 15 minutes
    await cache_set(cache_key, result.model_dump(mode="json"), ttl_seconds=900)
    return result


@router.get("/{city_slug}/picks/{pick_date}", response_model=DailyPicksResponse)
async def picks_by_date(
    city_slug: str,
    pick_date: date,
    db: AsyncSession = Depends(get_db),
) -> DailyPicksResponse:
    city = await _get_city(db, city_slug)
    return await _get_picks_for_date(db, city.id, pick_date)
