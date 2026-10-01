from pydantic import BaseModel

from app.schemas.event import EventSummaryResponse


class FeedResponse(BaseModel):
    success: bool = True
    data: list[EventSummaryResponse]
    next_cursor: str | None = None
    has_more: bool = False
