import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.schemas.story import (
    StoryClusterResponse,
    StoryDetailResponse,
    StorySummaryResponse,
)
from app.db.postgres import get_db
from app.models.story import Story
from app.models.topic import Topic
from app.services.events.story_clustering import StoryClusteringService

router = APIRouter(prefix="/stories", tags=["Stories"])
logger = logging.getLogger(__name__)


@router.get("", response_model=list[StorySummaryResponse])
async def list_stories(
    topic_id: str | None = Query(None, description="Filter stories by Topic ID"),
    domain_id: str | None = Query(None, description="Filter stories by Domain ID"),
    status_filter: str | None = Query(
        None, description="Filter by status (PENDING, VERIFIED, ARCHIVED)"
    ),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a list of Stories (long-running narratives) with event counts and verification states.
    """
    stmt = (
        select(Story)
        .options(
            selectinload(Story.topic).selectinload(Topic.domain),
            selectinload(Story.events),
        )
        .order_by(Story.updated_at.desc())
        .limit(limit)
    )

    if topic_id:
        stmt = stmt.where(Story.topic_id == topic_id)
    if status_filter:
        stmt = stmt.where(Story.status == status_filter)

    res = await db.execute(stmt)
    stories = res.scalars().all()

    output = []
    for s in stories:
        if domain_id and s.topic and s.topic.domain_id != domain_id:
            continue
        output.append(
            StorySummaryResponse(
                id=s.id,
                title=s.title,
                slug=s.slug,
                description=s.description,
                status=s.status,
                topic_id=s.topic_id,
                topic_name=s.topic.name if s.topic else None,
                domain_name=s.topic.domain.name if s.topic and s.topic.domain else None,
                event_count=len(s.events),
                created_at=s.created_at.isoformat(),
                updated_at=s.updated_at.isoformat(),
            )
        )
    return output


@router.get("/{story_id}", response_model=StoryDetailResponse)
async def get_story_detail(
    story_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns complete Story narrative dossier, including participating events in chronological order.
    """
    service = StoryClusteringService(db)
    story_detail = await service.get_story_timeline(story_id)
    if not story_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Story with ID '{story_id}' not found.",
        )
    return StoryDetailResponse(**story_detail)


@router.post("/cluster", response_model=StoryClusterResponse)
async def cluster_ungrouped_events(
    limit: int = Query(
        50, ge=1, le=200, description="Max ungrouped events to evaluate"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Evaluates UNGROUPED events, clusters them into long-running Stories,
    and checks Story verification consensus rules (>= 2 events with independent sources).
    """
    service = StoryClusteringService(db)
    result = await service.cluster_ungrouped_events(limit=limit)
    return StoryClusterResponse(
        grouped_count=result["grouped_count"],
        stories_created=result["stories_created"],
        stories_updated=result["stories_updated"],
        message=f"Clustering complete: {result['grouped_count']} events grouped into {result['stories_created']} new stories.",
    )
