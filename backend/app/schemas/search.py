from pydantic import BaseModel
from typing import List, Optional
from app.schemas.event import EventSummaryResponse


class SearchResultItem(BaseModel):
    id: str
    title: str
    category: str
    summary: Optional[str] = None
    knowledge_score: float
    verification_status: str


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[SearchResultItem]
