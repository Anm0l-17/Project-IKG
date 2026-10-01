from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.middleware.observability import metrics_collector
from app.models.event import Event
from app.models.relationship import EventRelationship
from app.models.source import Source
from app.models.story import Story

router = APIRouter(prefix="/metrics", tags=["Observability & Metrics"])


class MetricsResponse(BaseModel):
    telemetry: dict[str, Any]
    platform_stats: dict[str, Any]


@router.get("", response_model=MetricsResponse)
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """
    Returns telemetry metrics (latency, request counts, error rates) and
    knowledge platform database statistics (total events, verified events, stories, graph edges).
    """
    # 1. Telemetry
    telemetry = metrics_collector.get_summary()

    # 2. Platform entities count
    events_count = (await db.execute(select(func.count(Event.id)))).scalar() or 0
    verified_events_count = (
        await db.execute(
            select(func.count(Event.id)).where(Event.verification_status == "VERIFIED")
        )
    ).scalar() or 0
    stories_count = (await db.execute(select(func.count(Story.id)))).scalar() or 0
    relationships_count = (
        await db.execute(select(func.count(EventRelationship.id)))
    ).scalar() or 0
    sources_count = (await db.execute(select(func.count(Source.id)))).scalar() or 0

    platform_stats = {
        "total_events": events_count,
        "verified_events": verified_events_count,
        "developing_events": events_count - verified_events_count,
        "total_stories": stories_count,
        "total_graph_relationships": relationships_count,
        "active_sources": sources_count,
    }

    return MetricsResponse(
        telemetry=telemetry,
        platform_stats=platform_stats,
    )
