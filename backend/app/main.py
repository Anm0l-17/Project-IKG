from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logger import configure_logging, logger
from app.api.v1.health import router as health_router
from app.api.v1.feed import router as feed_router
from app.api.v1.event import router as event_router
from app.api.v1.timeline import router as timeline_router
from app.api.v1.category import router as category_router
from app.api.v1.search import router as search_router
from app.api.v1.graph import router as graph_router
from app.api.v1.story import router as story_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.metrics import router as metrics_router
from app.middleware.observability import ObservabilityMiddleware
from app.middleware.security import SecurityHeadersMiddleware, RateLimiterMiddleware


from app.db.postgres import engine
from app.workers.scheduler import ingestion_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting India Knowledge Graph Backend Service", env=settings.APP_ENV)
    ingestion_scheduler.start(interval_minutes=15)
    yield
    logger.info("Shutting down India Knowledge Graph Backend Service")
    ingestion_scheduler.shutdown()
    await engine.dispose()


app = FastAPI(
    title="India Knowledge Graph API",
    description="An AI-powered Event Intelligence & Verification Platform for Indian Affairs",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"] if settings.APP_ENV == "development" else []
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins if allow_origins else ["*"],
    allow_credentials=True if allow_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Middlewares (Order: Outer -> Inner)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware, max_requests=300, window_seconds=60)
app.add_middleware(ObservabilityMiddleware)

# Register API Routes
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(feed_router, prefix="/api/v1", tags=["Feed"])
app.include_router(event_router, prefix="/api/v1", tags=["Events"])
app.include_router(timeline_router, prefix="/api/v1", tags=["Timelines"])
app.include_router(category_router, prefix="/api/v1", tags=["Categories"])
app.include_router(search_router, prefix="/api/v1", tags=["Search"])
app.include_router(graph_router, prefix="/api/v1", tags=["Graph"])
app.include_router(story_router, prefix="/api/v1", tags=["Stories"])
app.include_router(tasks_router, prefix="/api/v1", tags=["Background Tasks"])
app.include_router(metrics_router, prefix="/api/v1", tags=["Observability & Metrics"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to India Knowledge Graph API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
