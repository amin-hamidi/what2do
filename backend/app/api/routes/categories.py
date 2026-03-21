from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

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
) -> list[CategoryResponse]:
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

    return [
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
