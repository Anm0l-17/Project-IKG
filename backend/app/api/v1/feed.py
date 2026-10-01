from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.repositories.postgres.event_repo import EventRepository
from app.schemas.event import EventSummaryResponse
from app.schemas.feed import FeedResponse

router = APIRouter()


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    category: str | None = Query(None, description="Category filter"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    repo = EventRepository(db)
    events = await repo.get_feed_events(category=category, limit=limit)

    event_dtos = [EventSummaryResponse.model_validate(e) for e in events]
    return FeedResponse(success=True, data=event_dtos, has_more=len(events) == limit)


@router.get("/feed/trending", response_model=FeedResponse)
async def get_trending_feed(
    limit: int = Query(10, ge=1, le=50), db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    events = await repo.get_trending_events(limit=limit)

    event_dtos = [EventSummaryResponse.model_validate(e) for e in events]
    return FeedResponse(success=True, data=event_dtos, has_more=False)
