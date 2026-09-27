import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.workers.dispatcher import task_dispatcher
from app.workers.tasks import (
    task_ingest_rss,
    task_verification_consensus,
    task_cluster_stories,
    task_backfill_embeddings,
)

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])
logger = logging.getLogger(__name__)


class TaskStatusResponse(BaseModel):
    queue_status: str
    distributed_queue: str
    backend: str
    message: Optional[str] = None
    redis_url: Optional[str] = None


class TriggerTaskRequest(BaseModel):
    task_name: str = Field(..., description="Task name: ingest_rss | verification_pass | cluster_stories | backfill_embeddings")
    limit: Optional[int] = Field(20, description="Optional batch/item limit")


class TriggerTaskResponse(BaseModel):
    status: str
    job_id: str
    backend: str
    task_name: str


@router.get("/status", response_model=TaskStatusResponse)
async def get_tasks_status():
    """
    Returns background task worker health and queue status.
    """
    health = await task_dispatcher.health_check()
    return TaskStatusResponse(
        queue_status=health.get("status", "unknown"),
        distributed_queue=health.get("distributed_queue", "unknown"),
        backend=health.get("backend", "unknown"),
        message=health.get("message") or health.get("error"),
        redis_url=health.get("redis_url"),
    )


@router.post("/trigger", response_model=TriggerTaskResponse)
async def trigger_task(req: TriggerTaskRequest):
    """
    Asynchronously triggers a background task via the unified task dispatcher (Redis/ARQ or in-process).
    """
    name = req.task_name.lower().strip()
    if name == "ingest_rss":
        res = await task_dispatcher.enqueue(
            "task_ingest_rss",
            task_ingest_rss,
            limit=req.limit or 20,
        )
    elif name == "verification_pass":
        res = await task_dispatcher.enqueue(
            "task_verification_consensus",
            task_verification_consensus,
        )
    elif name == "cluster_stories":
        res = await task_dispatcher.enqueue(
            "task_cluster_stories",
            task_cluster_stories,
            limit=req.limit or 50,
        )
    elif name == "backfill_embeddings":
        res = await task_dispatcher.enqueue(
            "task_backfill_embeddings",
            task_backfill_embeddings,
            batch_size=req.limit or 100,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown task '{req.task_name}'. Allowed: ingest_rss, verification_pass, cluster_stories, backfill_embeddings",
        )

    return TriggerTaskResponse(**res)
