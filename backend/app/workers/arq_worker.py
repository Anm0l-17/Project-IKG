import logging
from typing import ClassVar
from urllib.parse import urlparse

from arq.connections import RedisSettings

from app.core.config import settings
from app.workers.tasks import (
    task_backfill_embeddings,
    task_cluster_stories,
    task_infer_relationships,
    task_ingest_rss,
    task_verification_consensus,
)

logger = logging.getLogger(__name__)


def get_redis_settings() -> RedisSettings:
    parsed = urlparse(settings.REDIS_URL)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
    )


async def startup(ctx):
    logger.info("ARQ Distributed Background Worker started successfully.")


async def shutdown(ctx):
    logger.info("ARQ Distributed Background Worker shutting down.")


class WorkerSettings:
    """
    ARQ Worker Settings for running distributed background jobs.
    Run via: arq app.workers.arq_worker.WorkerSettings
    """

    functions: ClassVar[tuple] = (
        task_ingest_rss,
        task_verification_consensus,
        task_infer_relationships,
        task_cluster_stories,
        task_backfill_embeddings,
    )
    redis_settings = get_redis_settings()
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = 10
    poll_delay = 0.5
    job_timeout = 300
