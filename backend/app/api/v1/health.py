from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.postgres import get_db
from app.workers.dispatcher import task_dispatcher

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    llm_provider: str


class ReadinessResponse(BaseModel):
    status: str
    timestamp: str
    database: dict[str, Any]
    task_queue: dict[str, Any]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Liveness probe: verifies that the FastAPI application instance is running.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.APP_ENV,
        timestamp=datetime.now(UTC).isoformat(),
        llm_provider=settings.LLM_PROVIDER,
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    Readiness probe: validates database connectivity and background task runner health.
    Returns HTTP 200 if ready for traffic, HTTP 503 if any core dependency fails.
    """
    # 1. Check Database connectivity
    db_status = {"status": "unknown"}
    is_db_healthy = False
    try:
        await db.execute(text("SELECT 1;"))
        db_status = {"status": "connected", "type": "postgres_or_sqlite"}
        is_db_healthy = True
    except Exception as e:
        db_status = {"status": "unhealthy", "error": str(e)}

    # 2. Check Task Queue
    queue_status = await task_dispatcher.health_check()

    overall_status = "ready" if is_db_healthy else "degraded"
    if not is_db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status=overall_status,
        timestamp=datetime.now(UTC).isoformat(),
        database=db_status,
        task_queue=queue_status,
    )
