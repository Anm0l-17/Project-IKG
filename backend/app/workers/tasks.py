from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.db.postgres import AsyncSessionLocal
from app.services.events.candidate_generation import CandidateEventService
from app.services.events.story_clustering import StoryClusteringService
from app.services.events.verification import VerificationEngine
from app.services.graph.engine import GraphEngine
from app.services.ingestion.gktoday import GKTodayAdapter
from app.services.ingestion.indianexpress import IndianExpressAdapter
from app.services.ingestion.newsapi_fallback import NewsAPIFallbackAdapter
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.thehindu import TheHinduAdapter
from app.services.search.hybrid_search import HybridSearchService


@asynccontextmanager
async def _get_db(
    ctx: Any | None = None, db: AsyncSession | None = None
) -> AsyncGenerator[AsyncSession]:
    explicit_db = db or (ctx.get("db") if isinstance(ctx, dict) else None)
    if explicit_db is not None:
        yield explicit_db
    else:
        async with AsyncSessionLocal() as session:
            yield session


async def task_ingest_rss(
    ctx: Any | None = None, limit: int = 20, db: AsyncSession | None = None
) -> dict[str, Any]:
    """
    Background task: Ingest articles from trusted Indian RSS feeds, run deduplication,
    and generate candidate events.
    """
    logger.info("Executing background task: task_ingest_rss", limit=limit)
    async with _get_db(ctx, db) as session:
        pipeline = IngestionPipeline(session)
        adapters = [GKTodayAdapter(), TheHinduAdapter(), IndianExpressAdapter()]
        saved_articles = []

        for adapter in adapters:
            try:
                articles = await pipeline.ingest_from_adapter(adapter, limit=limit)
                saved_articles.extend(articles)
            except Exception as e:
                logger.error(f"Ingestion error for {adapter.source_name}: {e}")

        if not saved_articles:
            try:
                fallback = NewsAPIFallbackAdapter()
                articles = await pipeline.ingest_from_adapter(fallback, limit=limit)
                saved_articles.extend(articles)
            except Exception as e:
                logger.error(f"Fallback ingestion error: {e}")

        created_events_count = 0
        if saved_articles:
            candidate_service = CandidateEventService(session)
            events = await candidate_service.generate_candidates_from_articles(
                saved_articles
            )
            created_events_count = len(events)

        return {
            "articles_ingested": len(saved_articles),
            "events_created": created_events_count,
        }


async def task_verification_consensus(
    ctx: Any | None = None, db: AsyncSession | None = None
) -> dict[str, Any]:
    """
    Background task: Process the 10-day pending verification queue and expire uncorroborated events.
    """
    logger.info("Executing background task: task_verification_consensus")
    async with _get_db(ctx, db) as session:
        v_engine = VerificationEngine(session)
        expired_count = await v_engine.process_pending_queue_expirations()
        return {"expired_events_count": expired_count}


async def task_infer_relationships(
    ctx: Any | None = None, event_id: str = "", db: AsyncSession | None = None
) -> dict[str, Any]:
    """
    Background task: Compute deterministic graph relationships (PRECEDES, CAUSES, RELATED_TO) for an event.
    """
    logger.info(
        "Executing background task: task_infer_relationships", event_id=event_id
    )
    if not event_id:
        return {"relationships_created": 0}

    async with _get_db(ctx, db) as session:
        engine = GraphEngine(session)
        rels = await engine.infer_relationships_for_event(event_id)
        return {"event_id": event_id, "relationships_created": len(rels)}


async def task_cluster_stories(
    ctx: Any | None = None, limit: int = 50, db: AsyncSession | None = None
) -> dict[str, Any]:
    """
    Background task: Group ungrouped events into narrative Stories and evaluate verification status.
    """
    logger.info("Executing background task: task_cluster_stories", limit=limit)
    async with _get_db(ctx, db) as session:
        service = StoryClusteringService(session)
        result = await service.cluster_ungrouped_events(limit=limit)
        return result


async def task_backfill_embeddings(
    ctx: Any | None = None, batch_size: int = 100, db: AsyncSession | None = None
) -> dict[str, Any]:
    """
    Background task: Compute missing dense vector embeddings for events in background.
    """
    logger.info(
        "Executing background task: task_backfill_embeddings", batch_size=batch_size
    )
    async with _get_db(ctx, db) as session:
        service = HybridSearchService(session)
        count = await service.backfill_event_embeddings(batch_size=batch_size)
        return {"embeddings_backfilled": count}
