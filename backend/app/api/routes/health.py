from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
async def health_check() -> dict:
    return {"status": "healthy", "version": settings.APP_VERSION}


@router.get("/debug/db")
async def debug_db() -> dict:
    """Debug endpoint to check DB connectivity."""
    info = {
        "database_url_prefix": settings.DATABASE_URL[:30] + "...",
        "async_url_prefix": settings.ASYNC_DATABASE_URL[:40] + "...",
        "redis_url": settings.REDIS_URL[:30] + "...",
    }
    try:
        from app.db.session import async_session
        async with async_session() as db:
            result = await db.execute(__import__("sqlalchemy").text("SELECT 1"))
            info["db_connected"] = True
            info["db_result"] = str(result.scalar())
    except Exception as e:
        info["db_connected"] = False
        info["db_error"] = f"{type(e).__name__}: {str(e)[:200]}"
    return info
