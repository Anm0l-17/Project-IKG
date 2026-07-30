from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimelineEntryBase(BaseModel):
    event_id: str
    sequence: int
    title: str
    summary: str
    published_at: datetime
    importance: float = 1.0
    source_count: int = 1


class TimelineEntryResponse(TimelineEntryBase):
    id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
