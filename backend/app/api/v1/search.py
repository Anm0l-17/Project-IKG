from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.schemas.search import (
    BackfillEmbeddingsResponse,
    SearchResponse,
    SearchResultItem,
)
from app.services.search.hybrid_search import HybridSearchService

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_events(
    q: str = Query(..., min_length=1, description="Search query string"),
    mode: str = Query(
        "hybrid", description="Search mode: hybrid, semantic, or lexical"
    ),
    category: str | None = Query(None, description="Filter by event category"),
    verification_status: str | None = Query(
        None, description="Filter by verification status"
    ),
    topic_id: str | None = Query(None, description="Filter by topic ID"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
):
    """
    Search events using Hybrid (Lexical + Dense Vector Semantic) search with RRF scoring.
    Supports filtering by category, verification status, and topic.
    """
    service = HybridSearchService(db)
    result = await service.search(
        query=q,
        mode=mode,
        category=category,
        verification_status=verification_status,
        topic_id=topic_id,
        limit=limit,
        offset=offset,
    )

    items = [
        SearchResultItem(
            id=r["id"],
            title=r["title"],
            slug=r["slug"],
            category=r["category"],
            subcategory=r["subcategory"],
            summary=r["summary"],
            highlight_snippet=r["highlight_snippet"],
            knowledge_score=r["knowledge_score"],
            verification_status=r["verification_status"],
            grouping_status=r["grouping_status"],
            primary_story_id=r["primary_story_id"],
            topic_name=r["topic_name"],
            domain_name=r["domain_name"],
            first_seen=r["first_seen"],
            last_updated=r["last_updated"],
            relevance_score=r["relevance_score"],
            lexical_score=r["lexical_score"],
            semantic_score=r["semantic_score"],
            match_type=r["match_type"],
        )
        for r in result["results"]
    ]

    return SearchResponse(
        query=result["query"],
        mode=result["mode"],
        total_results=result["total_results"],
        results=items,
    )


@router.post("/search/backfill-embeddings", response_model=BackfillEmbeddingsResponse)
async def backfill_embeddings(
    batch_size: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Offline maintenance endpoint to backfill dense vector embeddings for events missing vectors.
    """
    service = HybridSearchService(db)
    count = await service.backfill_event_embeddings(batch_size=batch_size)
    return BackfillEmbeddingsResponse(
        updated_count=count,
        message=f"Successfully generated embeddings for {count} events.",
    )
