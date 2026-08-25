import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.postgres import AsyncSessionLocal
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.gktoday import GKTodayAdapter
from app.services.ingestion.thehindu import TheHinduAdapter
from app.services.ingestion.indianexpress import IndianExpressAdapter
from app.services.ingestion.newsapi_fallback import NewsAPIFallbackAdapter
from app.services.events.candidate_generation import CandidateEventService

logger = logging.getLogger(__name__)


async def run_scheduled_ingestion_job():
    """
    Scheduled job that runs RSS ingestion from primary sources and produces candidate events.
    """
    logger.info("Starting scheduled RSS ingestion job...")
    async with AsyncSessionLocal() as db:
        pipeline = IngestionPipeline(db)
        adapters = [GKTodayAdapter(), TheHinduAdapter(), IndianExpressAdapter()]
        saved_articles = []

        for adapter in adapters:
            try:
                articles = await pipeline.ingest_from_adapter(adapter, limit=20)
                saved_articles.extend(articles)
                logger.info(f"Ingested {len(articles)} articles from {adapter.source_name}")
            except Exception as e:
                logger.error(f"Scheduled ingestion error for {adapter.source_name}: {e}")

        # If primary adapters returned 0 articles, attempt fallback
        if not saved_articles:
            try:
                fallback = NewsAPIFallbackAdapter()
                fallback_articles = await pipeline.ingest_from_adapter(fallback, limit=20)
                saved_articles.extend(fallback_articles)
                logger.info(f"Ingested {len(fallback_articles)} articles from NewsAPI Fallback")
            except Exception as e:
                logger.error(f"Scheduled ingestion error for Fallback: {e}")

        if saved_articles:
            candidate_service = CandidateEventService(db)
            events = await candidate_service.generate_candidates_from_articles(saved_articles)
            logger.info(f"Scheduled ingestion created {len(events)} candidate events")
        else:
            logger.info("Scheduled ingestion finished with 0 new articles.")


async def run_scheduled_verification_pass():
    """
    Scheduled job that scans the 10-day pending queue and expires uncorroborated single-source events.
    """
    logger.info("Starting scheduled verification queue maintenance job...")
    async with AsyncSessionLocal() as db:
        from app.services.events.verification import VerificationEngine
        v_engine = VerificationEngine(db)
        expired_count = await v_engine.process_pending_queue_expirations()
        logger.info(f"Scheduled verification pass completed. Expired {expired_count} events.")


class IngestionScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self, interval_minutes: int = 15):
        self.scheduler.add_job(
            run_scheduled_ingestion_job,
            "interval",
            minutes=interval_minutes,
            id="rss_ingestion_job",
            replace_existing=True
        )
        self.scheduler.add_job(
            run_scheduled_verification_pass,
            "interval",
            minutes=interval_minutes * 2,
            id="verification_pass_job",
            replace_existing=True
        )
        self.scheduler.start()
        logger.info(f"IngestionScheduler started (ingestion: {interval_minutes}m, verification: {interval_minutes * 2}m)")

    def shutdown(self):
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("IngestionScheduler shutdown successfully.")


ingestion_scheduler = IngestionScheduler()
