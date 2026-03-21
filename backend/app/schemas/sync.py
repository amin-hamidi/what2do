from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SyncTriggerResponse(BaseModel):
    task_id: str
    source: str
    status: str


class SyncLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID | None = None
    action: str
    status: str
    events_found: int
    events_created: int
    events_updated: int
    events_deduplicated: int
    error: str | None = None
    duration_seconds: float | None = None
    started_at: datetime
    completed_at: datetime | None = None
