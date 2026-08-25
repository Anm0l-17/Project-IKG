from pydantic import BaseModel, ConfigDict, computed_field
from typing import Optional, List
from datetime import datetime
from app.schemas.timeline import TimelineEntryResponse
from app.models.enums import VerificationStatus, GroupingStatus, EventLifecycleState


class EventBase(BaseModel):
    canonical_title: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    summary: Optional[str] = None
    knowledge_score: float = 0.0
    importance_score: float = 0.0
    grouping_status: str = GroupingStatus.UNGROUPED.value
    verification_status: str = VerificationStatus.PENDING.value
    status: str = EventLifecycleState.PENDING.value


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
    grouping_status: str
    verification_status: str
    status: str
    first_seen: datetime
    last_updated: datetime

    @computed_field
    @property
    def is_developing(self) -> bool:
        """
        DEVELOPING is a derived user-facing trust label when verification_status is PENDING.
        """
        return self.verification_status == VerificationStatus.PENDING.value

    model_config = ConfigDict(from_attributes=True)


class EventDetailResponse(EventSummaryResponse):
    timeline_entries: List[TimelineEntryResponse] = []

    model_config = ConfigDict(from_attributes=True)

