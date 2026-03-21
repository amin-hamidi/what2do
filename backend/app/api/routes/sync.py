from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.db.models.city import City
from app.db.models.source import Source
from app.db.models.sync_log import SyncLog
from app.schemas.sync import SyncLogResponse, SyncTriggerResponse

router = APIRouter()


@router.post("/{city_slug}/sync/{source_name}", response_model=SyncTriggerResponse)
async def trigger_sync(
    city_slug: str,
    source_name: str,
    db: AsyncSession = Depends(get_db),
) -> SyncTriggerResponse:
    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    source_result = await db.execute(
        select(Source).where(Source.name == source_name, Source.is_active.is_(True))
    )
    source = source_result.scalar_one_or_none()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found or inactive")

    from app.worker import celery_app

    task = celery_app.send_task(
        "scrape_source",
        kwargs={"source_name": source_name, "city_slug": city_slug},
    )

    return SyncTriggerResponse(
        task_id=task.id,
        source=source_name,
        status="queued",
    )


@router.get("/{city_slug}/sync/status", response_model=list[SyncLogResponse])
async def sync_status(
    city_slug: str,
    db: AsyncSession = Depends(get_db),
) -> list[SyncLogResponse]:
    result = await db.execute(select(City).where(City.slug == city_slug))
    city = result.scalar_one_or_none()
    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    stmt = (
        select(SyncLog)
        .where(SyncLog.city_id == city.id)
        .order_by(SyncLog.started_at.desc())
        .limit(20)
    )
    rows = await db.execute(stmt)
    logs = rows.scalars().all()

    return [SyncLogResponse.model_validate(log) for log in logs]
