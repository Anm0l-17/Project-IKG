from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.event import EventSummaryResponse

class IngestionJobResponse(BaseModel):
    message: str = Field(..., description="Status message regarding the triggered ingestion job.")
    status: str = Field("PENDING", description="Background job status (e.g. PENDING, RUNNING).")


class IngestionResultResponse(BaseModel):
    articles_ingested: int
    events_created: int
    events_deduplicated: int
    errors: List[str] = []
    new_events: List[EventSummaryResponse]

