import logging
from typing import Any

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

logger = logging.getLogger(__name__)


async def task_ingest_rss(ctx: Any | None = None, limit: int = 20) -> dict[str, Any]:
    """
    Background task: Ingest articles from trusted Indian RSS feeds, run deduplication,
    and generate candidate events.
    """
    logger.info("Executing background task: task_ingest_rss", limit=limit)
    async with AsyncSessionLocal() as db:
        pipeline = IngestionPipeline(db)
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
            candidate_service = CandidateEventService(db)
            events = await candidate_service.generate_candidates_from_articles(
                saved_articles
            )
            created_events_count = len(events)

        return {
            "articles_ingested": len(saved_articles),
            "events_created": created_events_count,
        }


async def task_verification_consensus(ctx: Any | None = None) -> dict[str, Any]:
    """
    Background task: Process the 10-day pending verification queue and expire uncorroborated events.
    """
    logger.info("Executing background task: task_verification_consensus")
    async with AsyncSessionLocal() as db:
        v_engine = VerificationEngine(db)
        expired_count = await v_engine.process_pending_queue_expirations()
        return {"expired_events_count": expired_count}


async def task_infer_relationships(
    ctx: Any | None = None, event_id: str = ""
) -> dict[str, Any]:
    """
    Background task: Compute deterministic graph relationships (PRECEDES, CAUSES, RELATED_TO) for an event.
    """
    logger.info(
        "Executing background task: task_infer_relationships", event_id=event_id
    )
    if not event_id:
        return {"relationships_created": 0}

    async with AsyncSessionLocal() as db:
        engine = GraphEngine(db)
        rels = await engine.infer_relationships_for_event(event_id)
        return {"event_id": event_id, "relationships_created": len(rels)}


async def task_cluster_stories(
    ctx: Any | None = None, limit: int = 50
) -> dict[str, Any]:
    """
    Background task: Group ungrouped events into narrative Stories and evaluate verification status.
    """
    logger.info("Executing background task: task_cluster_stories", limit=limit)
    async with AsyncSessionLocal() as db:
        service = StoryClusteringService(db)
        result = await service.cluster_ungrouped_events(limit=limit)
        return result


async def task_backfill_embeddings(
    ctx: Any | None = None, batch_size: int = 100
) -> dict[str, Any]:
    """
    Background task: Compute missing dense vector embeddings for events in background.
    """
    logger.info(
        "Executing background task: task_backfill_embeddings", batch_size=batch_size
    )
    async with AsyncSessionLocal() as db:
        service = HybridSearchService(db)
        count = await service.backfill_event_embeddings(batch_size=batch_size)
        return {"embeddings_backfilled": count}
