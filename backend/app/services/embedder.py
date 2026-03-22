"""
Embedding service using sentence-transformers for event vector search.
Uses all-MiniLM-L6-v2 (384 dimensions, fast, good quality).
"""

from __future__ import annotations

import logging
from functools import lru_cache

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.event import Event

logger = logging.getLogger("what2do.embedder")

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def _get_model():
    """Lazy-load the sentence-transformer model (cached singleton)."""
    from sentence_transformers import SentenceTransformer
    logger.info("Loading embedding model: %s", MODEL_NAME)
    return SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """Generate a 384-dim embedding vector for the given text."""
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def _event_to_text(event: Event) -> str:
    """Build embedding text from event fields."""
    parts = [event.title]
    if event.description:
        parts.append(event.description[:500])
    if event.genre:
        parts.append(f"Genre: {event.genre}")
    if event.cuisine_type:
        parts.append(f"Cuisine: {event.cuisine_type}")
    if event.neighborhood:
        parts.append(f"Location: {event.neighborhood}")
    if event.tags:
        parts.append(f"Tags: {event.tags}")
    return " | ".join(parts)


async def embed_events(db: AsyncSession, limit: int = 200) -> int:
    """Embed events that don't have an embedding yet. Returns count embedded."""
    result = await db.execute(
        select(Event)
        .where(Event.embedding.is_(None), Event.status == "active")
        .limit(limit)
    )
    events = result.scalars().all()

    if not events:
        return 0

    model = _get_model()
    texts = [_event_to_text(e) for e in events]
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)

    for event, emb in zip(events, embeddings):
        event.embedding = emb.tolist()

    await db.commit()
    logger.info("Embedded %d events", len(events))
    return len(events)
