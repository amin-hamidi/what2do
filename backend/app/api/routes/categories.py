from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get, cache_set
from app.core.deps import get_db
from app.db.models.category import Category
from app.db.models.city import City
from app.db.models.event import Event
from app.schemas.common import CategoryResponse

router = APIRouter()


@router.get("/{city_slug}/categories", response_model=list[CategoryResponse])
async def list_categories(
    city_slug: str,
    db: AsyncSession = Depends(get_db),
):
    # Check cache
    cache_key = f"categories:{city_slug}"
    cached = await cache_get(cache_key)
    if cached is not None:
        return JSONResponse(content=cached)

    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    stmt = (
        select(
            Category,
            func.count(Event.id).label("event_count"),
        )
        .outerjoin(Event, (Event.category_id == Category.id) & (Event.city_id == city.id) & (Event.status == "active"))
        .group_by(Category.id)
        .order_by(Category.sort_order.asc())
    )

    rows = await db.execute(stmt)
    results = rows.all()

    data = [
        CategoryResponse(
            id=cat.id,
            slug=cat.slug,
            name=cat.name,
            icon=cat.icon,
            sort_order=cat.sort_order,
            event_count=count,
        )
        for cat, count in results
    ]

    # Cache for 5 minutes
    await cache_set(cache_key, [d.model_dump(mode="json") for d in data], ttl_seconds=300)
    return data
