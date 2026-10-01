import logging
import time
import uuid
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    In-memory metrics collector for telemetry, request latency, and throughput.
    """

    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.total_errors = 0
        self.status_codes: dict[int, int] = {}
        self.path_counts: dict[str, int] = {}
        self.total_latency_ms = 0.0

    def record_request(
        self, method: str, path: str, status_code: int, latency_ms: float
    ):
        self.total_requests += 1
        self.total_latency_ms += latency_ms
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1

        # Keep top-level route path (normalize query strings and trailing slashes)
        route_key = f"{method} {path.split('?')[0].rstrip('/') or '/'}"
        self.path_counts[route_key] = self.path_counts.get(route_key, 0) + 1

        if status_code >= 400:
            self.total_errors += 1

    def get_summary(self) -> dict[str, Any]:
        uptime_seconds = time.time() - self.start_time
        avg_latency = (
            self.total_latency_ms / self.total_requests
            if self.total_requests > 0
            else 0.0
        )
        return {
            "uptime_seconds": round(uptime_seconds, 2),
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "error_rate_percentage": round(
                (self.total_errors / self.total_requests * 100)
                if self.total_requests > 0
                else 0.0,
                2,
            ),
            "average_latency_ms": round(avg_latency, 2),
            "status_code_distribution": self.status_codes,
            "popular_routes": dict(
                sorted(self.path_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ),
        }


metrics_collector = MetricsCollector()


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Tracks request lifecycle, injects X-Request-ID, logs duration, and aggregates metrics.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        start_time = time.perf_counter()

        response: Response = await call_next(request)

        duration_ms = (time.perf_counter() - start_time) * 1000.0

        # Inject telemetry headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = f"{duration_ms:.2f}"

        # Record metrics
        metrics_collector.record_request(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            latency_ms=duration_ms,
        )

        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms:.2f}ms) [ReqID: {request_id}]"
        )

        return response
