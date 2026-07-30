from pydantic import BaseModel
from typing import List, Optional
from app.schemas.event import EventSummaryResponse


class FeedResponse(BaseModel):
    success: bool = True
    data: List[EventSummaryResponse]
    next_cursor: Optional[str] = None
    has_more: bool = False
