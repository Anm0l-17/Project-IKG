from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    id: str
    title: str
    slug: str
    category: str
    subcategory: str | None = None
    summary: str | None = None
    highlight_snippet: str | None = None
    knowledge_score: float
    verification_status: str
    grouping_status: str
    primary_story_id: str | None = None
    topic_name: str | None = None
    domain_name: str | None = None
    first_seen: str
    last_updated: str
    relevance_score: float = Field(
        ..., description="Overall combined relevance score [0..1]"
    )
    lexical_score: float = Field(
        0.0, description="Keyword / token overlap score [0..1]"
    )
    semantic_score: float = Field(
        0.0, description="Dense vector similarity score [0..1]"
    )
    match_type: str = Field(
        "HYBRID", description="Match kind: HYBRID | SEMANTIC | LEXICAL | RELEVANCE"
    )


class SearchResponse(BaseModel):
    query: str
    mode: str = "hybrid"
    total_results: int
    results: list[SearchResultItem]


class BackfillEmbeddingsResponse(BaseModel):
    updated_count: int
    message: str
