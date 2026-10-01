import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.graph import GraphResponse
from app.db.postgres import get_db
from app.services.graph.engine import GraphEngine

router = APIRouter(prefix="/graph", tags=["Graph"])
logger = logging.getLogger(__name__)


@router.get("", response_model=GraphResponse)
async def get_graph(
    domain_id: str | None = Query(None, description="Filter graph by Domain ID"),
    category: str | None = Query(None, description="Filter graph by Domain Category"),
    limit: int = Query(40, ge=5, le=150, description="Max event nodes to include"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a global overview slice of the Knowledge Graph including Events, Entities, and connecting edges.
    """
    engine = GraphEngine(db)
    graph_data = await engine.get_global_graph(
        domain_id=domain_id, category=category, limit=limit
    )
    return GraphResponse(**graph_data)


@router.get("/event/{event_id}", response_model=GraphResponse)
async def get_event_subgraph(
    event_id: str,
    depth: int = Query(1, ge=1, le=3, description="Subgraph traversal depth"),
    min_confidence: float = Query(
        0.5, ge=0.0, le=1.0, description="Minimum edge confidence"
    ),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns the ego-subgraph for an Event, including connected Events, Entities, and directed edges.
    """
    engine = GraphEngine(db)
    graph_data = await engine.get_event_subgraph(
        event_id=event_id, depth=depth, min_confidence=min_confidence
    )
    if not graph_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID '{event_id}' not found.",
        )
    return GraphResponse(**graph_data)


@router.post("/infer/{event_id}")
async def infer_event_relationships(
    event_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Executes deterministic graph edge inference rules (PRECEDES, CAUSES, RELATED_TO)
    for the specified event against candidate events.
    """
    engine = GraphEngine(db)
    inferred = await engine.infer_relationships_for_event(event_id)
    return {
        "event_id": event_id,
        "inferred_relationships_count": len(inferred),
        "relationships": [
            {
                "id": r.id,
                "source": r.source_event_id,
                "target": r.target_event_id,
                "type": r.relationship_type,
                "confidence": r.confidence,
                "reasoning": r.reasoning,
            }
            for r in inferred
        ],
    }
