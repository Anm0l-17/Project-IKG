import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Appends OWASP recommended security headers to all HTTP responses.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    In-memory sliding window rate limiter per client IP address.
    Default: 120 requests per minute per IP.
    Excludes /health, /ready, and /docs from strict throttling.
    """

    def __init__(self, app, max_requests: int = 120, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_records: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        if path in (
            "/api/v1/health",
            "/api/v1/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
        ):
            return await call_next(request)

        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - self.window_seconds

        # Prune older requests
        records = [ts for ts in self.request_records[client_ip] if ts > window_start]
        self.request_records[client_ip] = records

        if len(records) >= self.max_requests:
            logger.warning(
                "Rate limit exceeded for client IP", client_ip=client_ip, path=path
            )
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.max_requests} requests per {self.window_seconds}s allowed.",
                },
                headers={"Retry-After": str(self.window_seconds)},
            )

        self.request_records[client_ip].append(now)
        return await call_next(request)
