from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.repositories.postgres.event_repo import EventRepository
from app.schemas.search import SearchResponse, SearchResultItem

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_events(
    q: str = Query(..., min_length=2, description="Search query string"),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    matching_events = await repo.search_events(query=q, limit=limit)

    results = [
        SearchResultItem(
            id=e.id,
            title=e.canonical_title,
            category=e.category,
            summary=e.summary,
            knowledge_score=e.knowledge_score,
            verification_status=e.verification_status
        )
        for e in matching_events
    ]

    return SearchResponse(
        query=q,
        total_results=len(results),
        results=results
    )
