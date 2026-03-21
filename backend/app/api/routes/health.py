from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "version": settings.APP_VERSION}
