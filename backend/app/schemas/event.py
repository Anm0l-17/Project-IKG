from datetime import datetime

from pydantic import BaseModel, ConfigDict, computed_field

from app.models.enums import EventLifecycleState, GroupingStatus, VerificationStatus
from app.schemas.timeline import TimelineEntryResponse


class EventBase(BaseModel):
    canonical_title: str
    slug: str
    category: str
    subcategory: str | None = None
    summary: str | None = None
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
    subcategory: str | None = None
    summary: str | None = None
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
    timeline_entries: list[TimelineEntryResponse] = []

    model_config = ConfigDict(from_attributes=True)
