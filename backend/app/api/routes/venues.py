from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.db.models.city import City
from app.db.models.event import Event
from app.db.models.venue import Venue
from app.schemas.common import VenueResponse

router = APIRouter()


@router.get("/{city_slug}/venues", response_model=list[VenueResponse])
async def list_venues(
    city_slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[VenueResponse]:
    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    stmt = (
        select(
            Venue,
            func.count(Event.id).label("event_count"),
        )
        .where(Venue.city_id == city.id)
        .outerjoin(Event, (Event.venue_id == Venue.id) & (Event.status == "active"))
        .group_by(Venue.id)
        .order_by(Venue.name.asc())
    )

    rows = await db.execute(stmt)
    results = rows.all()

    return [
        VenueResponse(
            id=venue.id,
            city_id=venue.city_id,
            name=venue.name,
            slug=venue.slug,
            address=venue.address,
            neighborhood=venue.neighborhood,
            website_url=venue.website_url,
            venue_type=venue.venue_type,
            event_count=count,
        )
        for venue, count in results
    ]
