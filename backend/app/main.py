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


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("Starting India Knowledge Graph Backend Service", env=settings.APP_ENV)
    yield
    logger.info("Shutting down India Knowledge Graph Backend Service")


app = FastAPI(
    title="India Knowledge Graph API",
    description="An AI-powered Event Intelligence & Verification Platform for Indian Affairs",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routes
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(feed_router, prefix="/api/v1", tags=["Feed"])
app.include_router(event_router, prefix="/api/v1", tags=["Events"])
app.include_router(timeline_router, prefix="/api/v1", tags=["Timelines"])
app.include_router(category_router, prefix="/api/v1", tags=["Categories"])
app.include_router(search_router, prefix="/api/v1", tags=["Search"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to India Knowledge Graph API",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
