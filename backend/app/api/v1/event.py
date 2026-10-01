import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.event import IngestionJobResponse
from app.api.v1.schemas.graph import GraphResponse
from app.db.postgres import AsyncSessionLocal, get_db
from app.models.enums import EventLifecycleState, GroupingStatus, VerificationStatus
from app.models.event import Event
from app.repositories.postgres.event_repo import EventRepository
from app.schemas.event import EventDetailResponse, EventSummaryResponse
from app.services.events.candidate_generation import CandidateEventService
from app.services.graph.engine import GraphEngine
from app.services.ingestion.gktoday import GKTodayAdapter
from app.services.ingestion.indianexpress import IndianExpressAdapter
from app.services.ingestion.newsapi_fallback import NewsAPIFallbackAdapter
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.thehindu import TheHinduAdapter

router = APIRouter()
logger = logging.getLogger(__name__)


async def run_ingestion_background():
    """
    Offline/Background worker execution for RSS ingestion and candidate creation.
    """
    async with AsyncSessionLocal() as db:
        pipeline = IngestionPipeline(db)
        adapters = [GKTodayAdapter(), TheHinduAdapter(), IndianExpressAdapter()]
        saved_articles = []
        errors = []

        for adapter in adapters:
            try:
                articles = await pipeline.ingest_from_adapter(adapter, limit=20)
                saved_articles.extend(articles)
            except Exception as e:
                logger.error(f"Ingestion failed for {adapter.source_name}: {e}")
                errors.append(f"Failed {adapter.source_name}: {e!s}")

        if not saved_articles and errors:
            try:
                fallback = NewsAPIFallbackAdapter()
                fallback_articles = await pipeline.ingest_from_adapter(
                    fallback, limit=20
                )
                saved_articles.extend(fallback_articles)
            except Exception as e:
                logger.error(f"Fallback ingestion failed: {e}")

        candidate_service = CandidateEventService(db)
        await candidate_service.generate_candidates_from_articles(saved_articles)


@router.get(
    "/events/{id}",
    response_model=EventDetailResponse,
    summary="Get Event Details",
    description="Retrieve a single Event by ID including its timeline entries and verified evidence.",
    responses={404: {"description": "The requested event does not exist."}},
)
async def get_event(id: str, db: AsyncSession = Depends(get_db)):
    repo = EventRepository(db)
    event = await repo.get_by_id(id, load_timeline=True)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested event does not exist.",
        )

    return EventDetailResponse.model_validate(event)


@router.post(
    "/events/ingest",
    response_model=IngestionJobResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Offline Ingestion Job",
    description="Triggers the RSS ingestion and candidate event creation process asynchronously in a background task.",
)
async def trigger_ingestion(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion_background)
    return IngestionJobResponse(
        message="Ingestion pipeline triggered successfully in background.",
        status="PENDING",
    )


@router.get(
    "/events",
    response_model=list[EventSummaryResponse],
    summary="List Events",
    description="Lists events with optional filtering by verification status or grouping status.",
)
async def list_events(
    verification_status: str | None = Query(
        None,
        description="Filter by verification status (PENDING, VERIFIED, REJECTED, ARCHIVED)",
    ),
    grouping_status: str | None = Query(
        None, description="Filter by grouping status (UNGROUPED, GROUPED)"
    ),
    status_filter: str | None = Query(
        None,
        alias="status",
        description="Filter by internal state (e.g. PENDING, VERIFIED, ACTIVE, HISTORICAL)",
    ),
    limit: int = Query(50, ge=1, le=100, description="Number of results to return"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Event).order_by(Event.created_at.desc()).limit(limit)

    if verification_status:
        valid_v_statuses = [s.value for s in VerificationStatus]
        if verification_status not in valid_v_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid verification_status. Must be one of: {valid_v_statuses}",
            )
        stmt = stmt.where(Event.verification_status == verification_status)

    if grouping_status:
        valid_g_statuses = [s.value for s in GroupingStatus]
        if grouping_status not in valid_g_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid grouping_status. Must be one of: {valid_g_statuses}",
            )
        stmt = stmt.where(Event.grouping_status == grouping_status)

    if status_filter:
        valid_states = [s.value for s in EventLifecycleState]
        if status_filter not in valid_states:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {valid_states}",
            )
        stmt = stmt.where(Event.status == status_filter)

    res = await db.execute(stmt)
    events = res.scalars().all()

    return [EventSummaryResponse.model_validate(ev) for ev in events]


@router.get("/events/{id}/graph", response_model=GraphResponse)
async def get_event_graph_subgraph(
    id: str,
    depth: int = Query(1, ge=1, le=3, description="Subgraph traversal depth"),
    min_confidence: float = Query(
        0.5, ge=0.0, le=1.0, description="Minimum edge confidence"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns ego-subgraph for an Event (Events, Entities, and directed edges).
    """
    engine = GraphEngine(db)
    graph_data = await engine.get_event_subgraph(
        event_id=id, depth=depth, min_confidence=min_confidence
    )
    if not graph_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID '{id}' not found.",
        )
    return GraphResponse(**graph_data)
