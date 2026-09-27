from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class StoryTimelineItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sequence: int
    event_id: str
    title: str
    category: str
    first_seen: str
    verification_status: str
    summary: Optional[str] = None
    sources: List[str] = []
    source_count: int = 0


class StorySummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    slug: str
    description: Optional[str] = None
    status: str
    topic_id: str
    topic_name: Optional[str] = None
    domain_name: Optional[str] = None
    event_count: int = 0
    created_at: str
    updated_at: str


class StoryDetailResponse(StorySummaryResponse):
    model_config = ConfigDict(from_attributes=True)

    sources: List[str] = []
    source_count: int = 0
    timeline: List[StoryTimelineItem] = []


class StoryClusterResponse(BaseModel):
    grouped_count: int
    stories_created: int
    stories_updated: int
    message: str
