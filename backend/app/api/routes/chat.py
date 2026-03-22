from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.db.models.city import City
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.event import EventResponse
from app.services.ai_chat import chat_with_events

router = APIRouter()


def _event_to_response(event) -> EventResponse:
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


@router.post("/{city_slug}/chat", response_model=ChatResponse)
async def chat(
    city_slug: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
) -> ChatResponse:
    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    response_text, matched_events = await chat_with_events(
        db=db,
        city_id=city.id,
        city_name=city.name,
        message=request.message,
        history=request.history,
    )

    return ChatResponse(
        message=response_text,
        events=[_event_to_response(e) for e in matched_events],
    )
