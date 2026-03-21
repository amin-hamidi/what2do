from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.event import EventResponse


class AIPickResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: UUID
    pick_date: date
    pick_type: str
    rank: int
    ai_blurb: str
    event: EventResponse | None = None


class DailyPicksResponse(BaseModel):
    top_pick: AIPickResponse | None = None
    categories: dict[str, list[AIPickResponse]] = {}
