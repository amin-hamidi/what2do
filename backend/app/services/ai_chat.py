"""
RAG Chat service — embeds user query, searches events via pgvector similarity,
and generates a conversational response with Claude.
"""

from __future__ import annotations

import logging

import anthropic
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.models.event import Event
from app.services.embedder import generate_embedding

logger = logging.getLogger("what2do.ai_chat")

SYSTEM_PROMPT = """\
You are What2Do, a friendly and knowledgeable event assistant for {city_name}. \
You help people discover the best events, restaurants, concerts, activities, \
sports games, and nightlife in the area.

Rules:
- Answer based on the events provided in context. Do not make up events.
- Always mention specific event names, dates, venues, and include the source URL when relevant.
- Be enthusiastic but concise — 2-4 sentences for simple questions, more for detailed requests.
- If no matching events exist in context, say so honestly and suggest browsing categories.
- You can suggest multiple events when appropriate.
- Format event names in bold when mentioning them.
"""


def _format_event_context(events: list[Event]) -> str:
    """Format matched events as context for Claude."""
    if not events:
        return "No matching events found in the database."

    parts = []
    for i, e in enumerate(events, 1):
        lines = [f"{i}. **{e.title}**"]
        if e.starts_at:
            lines.append(f"   Date: {e.starts_at.strftime('%A, %B %d at %I:%M %p')}")
        if e.venue:
            lines.append(f"   Venue: {e.venue.name}")
        elif e.neighborhood:
            lines.append(f"   Area: {e.neighborhood}")
        if e.description:
            lines.append(f"   About: {e.description[:200]}")
        if e.price_level:
            lines.append(f"   Price: {e.price_level}")
        if e.category:
            lines.append(f"   Category: {e.category.name}")
        lines.append(f"   Link: {e.source_url}")
        parts.append("\n".join(lines))

    return "\n\n".join(parts)


async def chat_with_events(
    db: AsyncSession,
    city_id,
    city_name: str,
    message: str,
    history: list[dict] | None = None,
) -> tuple[str, list[Event]]:
    """
    RAG chat: embed query → vector search → Claude response.

    Returns (response_text, matched_events).
    """
    settings = get_settings()

    # Step 1: Find relevant events via vector similarity
    matched_events = await _search_events(db, city_id, message, limit=8)

    # Step 2: Build prompt with event context
    context = _format_event_context(matched_events)

    system = SYSTEM_PROMPT.format(city_name=city_name)
    system += f"\n\nHere are the relevant events from our database:\n\n{context}"

    # Build message history
    messages = []
    if history:
        for h in history[-6:]:  # Keep last 6 messages for context
            messages.append({
                "role": h.get("role", "user"),
                "content": h.get("content", ""),
            })
    messages.append({"role": "user", "content": message})

    if not settings.ANTHROPIC_API_KEY:
        # Fallback without AI
        if matched_events:
            event_names = ", ".join(e.title for e in matched_events[:3])
            return (
                f"I found some events that might interest you: {event_names}. "
                "Check them out below! (AI responses require an API key to be configured.)",
                matched_events,
            )
        return (
            "I couldn't find events matching your query. Try browsing the category pages! "
            "(AI responses require an API key to be configured.)",
            [],
        )

    # Step 3: Call Claude
    client = anthropic.AsyncAnthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        timeout=30.0,
    )

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            system=system,
            messages=messages,
        )
        response_text = response.content[0].text
    except anthropic.APIError as exc:
        logger.error("Claude API error in chat: %s", exc)
        if matched_events:
            event_names = ", ".join(e.title for e in matched_events[:3])
            return (
                f"I found some relevant events: {event_names}. "
                "Check them out below!",
                matched_events,
            )
        return ("Sorry, I'm having trouble right now. Try browsing events directly!", [])

    return response_text, matched_events


async def _search_events(
    db: AsyncSession,
    city_id,
    query: str,
    limit: int = 8,
) -> list[Event]:
    """Search events using pgvector cosine similarity."""
    try:
        query_embedding = generate_embedding(query)
    except Exception:
        logger.exception("Failed to generate query embedding")
        return await _fallback_text_search(db, city_id, query, limit)

    # Use pgvector cosine distance operator <=>
    stmt = (
        select(Event)
        .where(
            Event.city_id == city_id,
            Event.status == "active",
            Event.embedding.isnot(None),
        )
        .options(
            selectinload(Event.venue),
            selectinload(Event.category),
            selectinload(Event.source),
        )
        .order_by(Event.embedding.cosine_distance(query_embedding))
        .limit(limit)
    )

    result = await db.execute(stmt)
    events = list(result.scalars().unique().all())

    # If no embeddings exist, fall back to text search
    if not events:
        return await _fallback_text_search(db, city_id, query, limit)

    return events


async def _fallback_text_search(
    db: AsyncSession,
    city_id,
    query: str,
    limit: int = 8,
) -> list[Event]:
    """Fallback text search when no embeddings are available."""
    search = f"%{query}%"
    stmt = (
        select(Event)
        .where(
            Event.city_id == city_id,
            Event.status == "active",
            (Event.title.ilike(search) | Event.description.ilike(search)),
        )
        .options(
            selectinload(Event.venue),
            selectinload(Event.category),
            selectinload(Event.source),
        )
        .order_by(Event.starts_at.asc().nullslast())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())
