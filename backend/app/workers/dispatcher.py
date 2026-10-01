import asyncio
import logging
from collections.abc import Callable
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class TaskDispatcher:
    """
    Unified background task dispatcher.
    Attempts to enqueue tasks to Redis via ARQ if Redis is available;
    otherwise falls back to asynchronous in-process execution.
    """

    def __init__(self):
        self._arq_pool = None
        self._redis_available = False

    async def get_redis_pool(self):
        """Lazy connection to ARQ Redis pool."""
        if self._arq_pool is not None:
            return self._arq_pool

        try:
            from urllib.parse import urlparse

            from arq import create_pool
            from arq.connections import RedisSettings

            parsed = urlparse(settings.REDIS_URL)
            host = parsed.hostname or "localhost"
            port = parsed.port or 6379
            database = int(parsed.path.lstrip("/") or "0")

            redis_settings = RedisSettings(host=host, port=port, database=database)
            self._arq_pool = await create_pool(redis_settings)
            self._redis_available = True
            logger.info(
                "Successfully connected to Redis ARQ task pool", host=host, port=port
            )
            return self._arq_pool
        except Exception as e:
            self._redis_available = False
            self._arq_pool = None
            logger.warning(
                "Redis unavailable for background task queue; using in-process async fallback.",
                error=str(e),
            )
            return None

    async def enqueue(
        self,
        task_name: str,
        async_func: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Dispatches a task. Uses ARQ if Redis is reachable, otherwise spawns an asyncio background task.
        """
        pool = await self.get_redis_pool()

        if pool is not None:
            try:
                job = await pool.enqueue_job(task_name, *args, **kwargs)
                logger.info(
                    f"Enqueued distributed task '{task_name}' [Job ID: {job.job_id}]"
                )
                return {
                    "status": "ENQUEUED_DISTRIBUTED",
                    "job_id": job.job_id,
                    "backend": "redis_arq",
                    "task_name": task_name,
                }
            except Exception as e:
                logger.warning(
                    f"Failed to enqueue to Redis ARQ ({e}); falling back to local task."
                )

        # Fallback to in-process background task
        task_id = f"local_{task_name}_{asyncio.get_event_loop().time()}"
        asyncio.create_task(
            self._run_with_logging(task_name, async_func, *args, **kwargs)
        )
        return {
            "status": "DISPATCHED_IN_PROCESS",
            "job_id": task_id,
            "backend": "in_process_asyncio",
            "task_name": task_name,
        }

    @staticmethod
    async def _run_with_logging(
        task_name: str, func: Callable, *args: Any, **kwargs: Any
    ):
        logger.info(f"[In-Process Background Task] Started '{task_name}'")
        try:
            result = await func(*args, **kwargs)
            logger.info(
                f"[In-Process Background Task] Succeeded '{task_name}'",
                result=str(result)[:200],
            )
        except Exception as e:
            logger.error(
                f"[In-Process Background Task] Failed '{task_name}': {e}", exc_info=True
            )

    async def health_check(self) -> dict[str, Any]:
        """Checks background task runner health and connectivity."""
        pool = await self.get_redis_pool()
        if pool is not None:
            try:
                pong = await pool.ping()
                return {
                    "status": "healthy",
                    "distributed_queue": "connected",
                    "backend": "redis_arq",
                    "redis_url": settings.REDIS_URL,
                }
            except Exception as e:
                return {
                    "status": "degraded",
                    "distributed_queue": "disconnected",
                    "backend": "in_process_fallback",
                    "error": str(e),
                }
        return {
            "status": "standalone",
            "distributed_queue": "standalone",
            "backend": "in_process_fallback",
            "message": "Redis not reachable; in-process async queue active.",
        }


task_dispatcher = TaskDispatcher()
