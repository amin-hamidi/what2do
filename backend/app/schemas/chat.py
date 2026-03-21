from pydantic import BaseModel

from app.schemas.event import EventResponse


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    message: str
    events: list[EventResponse] = []
