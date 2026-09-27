from pydantic import BaseModel, Field
from typing import List, Optional


class SearchResultItem(BaseModel):
    id: str
    title: str
    slug: str
    category: str
    subcategory: Optional[str] = None
    summary: Optional[str] = None
    highlight_snippet: Optional[str] = None
    knowledge_score: float
    verification_status: str
    grouping_status: str
    primary_story_id: Optional[str] = None
    topic_name: Optional[str] = None
    domain_name: Optional[str] = None
    first_seen: str
    last_updated: str
    relevance_score: float = Field(..., description="Overall combined relevance score [0..1]")
    lexical_score: float = Field(0.0, description="Keyword / token overlap score [0..1]")
    semantic_score: float = Field(0.0, description="Dense vector similarity score [0..1]")
    match_type: str = Field("HYBRID", description="Match kind: HYBRID | SEMANTIC | LEXICAL | RELEVANCE")


class SearchResponse(BaseModel):
    query: str
    mode: str = "hybrid"
    total_results: int
    results: List[SearchResultItem]


class BackfillEmbeddingsResponse(BaseModel):
    updated_count: int
    message: str
