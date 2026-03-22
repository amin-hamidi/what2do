"""
Redis cache utility for hot endpoint responses.
"""

from __future__ import annotations

import json
import logging

import redis.asyncio as aioredis

from app.core.config import get_settings

logger = logging.getLogger("what2do.cache")

_pool: aioredis.Redis | None = None


def _get_redis() -> aioredis.Redis:
    global _pool
    if _pool is None:
        settings = get_settings()
        _pool = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _pool


async def cache_get(key: str) -> dict | list | None:
    """Get a cached value by key. Returns None on miss or error."""
    try:
        r = _get_redis()
        raw = await r.get(f"w2d:{key}")
        if raw is not None:
            return json.loads(raw)
    except Exception:
        logger.debug("Cache miss/error for key: %s", key)
    return None


async def cache_set(key: str, data, ttl_seconds: int = 300) -> None:
    """Set a cached value with TTL."""
    try:
        r = _get_redis()
        await r.set(f"w2d:{key}", json.dumps(data, default=str), ex=ttl_seconds)
    except Exception:
        logger.debug("Cache set error for key: %s", key)


async def cache_invalidate(pattern: str = "*") -> None:
    """Invalidate cached keys matching a pattern."""
    try:
        r = _get_redis()
        keys = []
        async for key in r.scan_iter(f"w2d:{pattern}"):
            keys.append(key)
        if keys:
            await r.delete(*keys)
            logger.info("Invalidated %d cache keys matching: %s", len(keys), pattern)
    except Exception:
        logger.debug("Cache invalidation error for pattern: %s", pattern)
