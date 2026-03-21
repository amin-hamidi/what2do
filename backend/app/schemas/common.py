from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    state: str
    timezone: str
    is_active: bool


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    slug: str
    name: str
    icon: str | None = None
    sort_order: int
    event_count: int | None = None


class VenueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    city_id: UUID
    name: str
    slug: str
    address: str | None = None
    neighborhood: str | None = None
    website_url: str | None = None
    venue_type: str | None = None
    event_count: int | None = None


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    source_type: str
    is_active: bool
    last_scraped_at: datetime | None = None
