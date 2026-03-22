"""
AI Curator — uses Claude to generate daily event picks and blurbs.
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timedelta, timezone

import anthropic
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import get_settings
from app.db.models.ai_pick import AIPick
from app.db.models.category import Category
from app.db.models.city import City
from app.db.models.event import Event

logger = logging.getLogger("what2do.ai_curator")

CURATION_PROMPT = """\
You are What2Do's AI curator for {city_name}. Your job is to pick the most exciting, \
interesting, and noteworthy events for today.

Here are the upcoming events (next 48 hours):

{events_text}

Based on these events, create curated picks in the following JSON format:
{{
  "top_pick": {{
    "event_index": <int>,
    "blurb": "<1-2 sentence enthusiastic description of why this is THE event of the day>"
  }},
  "category_picks": [
    {{
      "category": "<category_slug>",
      "event_index": <int>,
      "blurb": "<1-2 sentence description of why this event stands out>"
    }}
  ]
}}

Rules:
- Pick exactly 1 top_pick — the single best event of the day
- Pick 1-2 events per category (only categories that have events)
- event_index refers to the number in the event list above (starting from 0)
- Blurbs should be engaging, specific, and mention what makes the event special
- Do NOT repeat the top_pick in category_picks
- Only output valid JSON, nothing else
"""


def _format_event(idx: int, event: Event) -> str:
    """Format an event for the Claude prompt."""
    parts = [f"[{idx}] {event.title}"]
    if event.category:
        parts.append(f"Category: {event.category.name}")
    if event.starts_at:
        parts.append(f"Date: {event.starts_at.strftime('%A, %B %d at %I:%M %p')}")
    if event.venue:
        parts.append(f"Venue: {event.venue.name}")
    if event.neighborhood:
        parts.append(f"Area: {event.neighborhood}")
    if event.description:
        parts.append(f"Description: {event.description[:200]}")
    if event.price_level:
        parts.append(f"Price: {event.price_level}")
    return " | ".join(parts)


async def curate_daily_picks(
    db: AsyncSession,
    city_id,
    pick_date: date,
) -> dict:
    """
    Generate AI-curated daily picks using Claude.

    Returns dict with counts: top_pick, category_picks created.
    """
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set, skipping curation")
        return {"status": "skipped", "reason": "no_api_key"}

    # Get city name
    city_result = await db.execute(select(City).where(City.id == city_id))
    city = city_result.scalar_one_or_none()
    city_name = city.name if city else "Dallas"

    # Query upcoming events (next 48h window)
    now = datetime.now(timezone.utc)
    window_end = now + timedelta(hours=48)

    stmt = (
        select(Event)
        .where(
            Event.city_id == city_id,
            Event.status == "active",
        )
        .options(
            selectinload(Event.venue),
            selectinload(Event.category),
        )
        .order_by(Event.starts_at.asc().nullslast())
        .limit(50)
    )

    result = await db.execute(stmt)
    events = list(result.scalars().unique().all())

    if not events:
        logger.info("No upcoming events found for curation")
        return {"status": "no_events"}

    # Format events for prompt
    events_text = "\n".join(_format_event(i, e) for i, e in enumerate(events))

    prompt = CURATION_PROMPT.format(
        city_name=city_name,
        events_text=events_text,
    )

    # Call Claude
    client = anthropic.AsyncAnthropic(
        api_key=settings.ANTHROPIC_API_KEY,
        timeout=60.0,
    )

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text.strip()

        # Parse JSON from response (handle markdown code blocks)
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        response_text = response_text.strip()

        picks_data = json.loads(response_text)

    except (json.JSONDecodeError, IndexError, KeyError) as exc:
        logger.error("Failed to parse Claude curation response: %s", exc)
        return {"status": "parse_error", "error": str(exc)}
    except anthropic.APIError as exc:
        logger.error("Claude API error during curation: %s", exc)
        return {"status": "api_error", "error": str(exc)}

    # Delete existing picks for this date
    await db.execute(
        delete(AIPick).where(
            AIPick.city_id == city_id,
            AIPick.pick_date == pick_date,
        )
    )

    created = 0

    # Create top pick
    top = picks_data.get("top_pick", {})
    top_idx = top.get("event_index", 0)
    if 0 <= top_idx < len(events):
        pick = AIPick(
            city_id=city_id,
            event_id=events[top_idx].id,
            pick_date=pick_date,
            pick_type="top_pick",
            rank=1,
            ai_blurb=top.get("blurb", "Today's top pick!"),
        )
        db.add(pick)
        created += 1

    # Create category picks
    for i, cat_pick in enumerate(picks_data.get("category_picks", [])):
        idx = cat_pick.get("event_index", 0)
        if 0 <= idx < len(events):
            pick = AIPick(
                city_id=city_id,
                event_id=events[idx].id,
                pick_date=pick_date,
                pick_type=cat_pick.get("category", "activities"),
                rank=i + 1,
                ai_blurb=cat_pick.get("blurb", "Worth checking out!"),
            )
            db.add(pick)
            created += 1

    await db.commit()
    logger.info("Created %d AI picks for %s", created, pick_date)
    return {"status": "completed", "picks_created": created}


WEEKEND_PROMPT = """\
You are What2Do's weekend planner for {city_name}. Create an exciting weekend itinerary \
using these available events:

{events_text}

Create a JSON weekend plan:
{{
  "saturday": {{
    "morning": {{"event_index": <int>, "blurb": "<why this is a great morning activity>"}},
    "afternoon": {{"event_index": <int>, "blurb": "<why this fits the afternoon>"}},
    "evening": {{"event_index": <int>, "blurb": "<perfect evening pick>"}}
  }},
  "sunday": {{
    "morning": {{"event_index": <int>, "blurb": "<relaxed sunday morning pick>"}},
    "afternoon": {{"event_index": <int>, "blurb": "<afternoon activity>"}},
    "evening": {{"event_index": <int>, "blurb": "<wrap up the weekend>"}}
  }}
}}

Rules:
- Use different events for each slot (no repeats)
- If not enough events, use null for that slot
- Blurbs should be 1 sentence, enthusiastic, and explain why it fits that time slot
- Only output valid JSON
"""


async def curate_weekend_plan(
    db: AsyncSession,
    city_id,
    saturday_date: date,
) -> dict:
    """Generate AI-curated weekend itinerary."""
    settings = get_settings()
    if not settings.ANTHROPIC_API_KEY:
        return {"status": "skipped", "reason": "no_api_key"}

    city_result = await db.execute(select(City).where(City.id == city_id))
    city = city_result.scalar_one_or_none()
    city_name = city.name if city else "Dallas"

    sunday_date = saturday_date + timedelta(days=1)

    # Get events for the weekend
    sat_start = datetime.combine(saturday_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    sun_end = datetime.combine(sunday_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    stmt = (
        select(Event)
        .where(Event.city_id == city_id, Event.status == "active")
        .options(selectinload(Event.venue), selectinload(Event.category))
        .order_by(Event.starts_at.asc().nullslast())
        .limit(30)
    )

    result = await db.execute(stmt)
    events = list(result.scalars().unique().all())

    if len(events) < 3:
        return {"status": "not_enough_events"}

    events_text = "\n".join(_format_event(i, e) for i, e in enumerate(events))
    prompt = WEEKEND_PROMPT.format(city_name=city_name, events_text=events_text)

    client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=60.0)

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = response.content[0].text.strip()
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        plan = json.loads(response_text.strip())
    except Exception as exc:
        logger.error("Weekend plan generation failed: %s", exc)
        return {"status": "error", "error": str(exc)}

    # Delete existing weekend picks
    await db.execute(
        delete(AIPick).where(
            AIPick.city_id == city_id,
            AIPick.pick_date == saturday_date,
            AIPick.pick_type.in_(["weekend_saturday", "weekend_sunday"]),
        )
    )

    created = 0
    for day_key, pick_type, day_date in [
        ("saturday", "weekend_saturday", saturday_date),
        ("sunday", "weekend_sunday", sunday_date),
    ]:
        day_plan = plan.get(day_key, {})
        for rank, slot in enumerate(["morning", "afternoon", "evening"], 1):
            slot_data = day_plan.get(slot)
            if not slot_data or slot_data.get("event_index") is None:
                continue
            idx = slot_data["event_index"]
            if 0 <= idx < len(events):
                pick = AIPick(
                    city_id=city_id,
                    event_id=events[idx].id,
                    pick_date=day_date,
                    pick_type=pick_type,
                    rank=rank,
                    ai_blurb=slot_data.get("blurb", "Great pick!"),
                )
                db.add(pick)
                created += 1

    await db.commit()
    logger.info("Created %d weekend picks", created)
    return {"status": "completed", "picks_created": created}
