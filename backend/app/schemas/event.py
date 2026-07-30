from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.timeline import TimelineEntryResponse


class EventBase(BaseModel):
    canonical_title: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    summary: Optional[str] = None
    knowledge_score: float = 0.0
    importance_score: float = 0.0
    verification_status: str = "Pending"
    status: str = "Candidate"


class EventCreate(EventBase):
    pass


class EventSummaryResponse(BaseModel):
    id: str
    canonical_title: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    summary: Optional[str] = None
    knowledge_score: float
    verification_status: str
    status: str
    first_seen: datetime
    last_updated: datetime

    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventSummaryResponse):
    timeline_entries: List[TimelineEntryResponse] = []

    model_config = ConfigDict(from_attributes=True)
