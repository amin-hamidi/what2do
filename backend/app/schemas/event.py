from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    title: str
    description: str | None = None
    short_description: str | None = None
    image_url: str | None = None
    source_url: str
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_all_day: bool = False
    tags: str | None = None
    price_level: str | None = None
    price_min: float | None = None
    price_max: float | None = None
    genre: str | None = None
    cuisine_type: str | None = None
    neighborhood: str | None = None
    status: str = "active"


class EventResponse(EventBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    city_id: UUID
    category_id: UUID
    venue_id: UUID | None = None
    source_id: UUID
    slug: str
    content_hash: str
    created_at: datetime
    scraped_at: datetime

    # Joined fields populated from relationships
    venue_name: str | None = None
    category_name: str | None = None
    source_name: str | None = None


class EventListResponse(BaseModel):
    items: list[EventResponse]
    total: int
    cursor: str | None = None


class EventFilters(BaseModel):
    category: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    venue_id: str | None = None
    neighborhood: str | None = None
    genre: str | None = None
    cuisine_type: str | None = None
    price_level: str | None = None
    tags: str | None = None
    q: str | None = None
    cursor: str | None = None
    limit: int = 20
