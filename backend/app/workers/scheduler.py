from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.postgres import AsyncSessionLocal
from app.services.ingestion import (
    IngestionPipeline,
    GKTodayAdapter,
    TheHinduAdapter,
    IndianExpressAdapter,
)

scheduler = AsyncIOScheduler()


async def scheduled_rss_ingestion_job():
    """
    Periodic background job running every 30 minutes to poll V1 RSS sources.
    Non-blocking async execution.
    """
    async with AsyncSessionLocal() as session:
        pipeline = IngestionPipeline(session)
        adapters = [
            GKTodayAdapter(),
            TheHinduAdapter(),
            IndianExpressAdapter(),
        ]
        for adapter in adapters:
            try:
                await pipeline.ingest_from_adapter(adapter, limit=30)
            except Exception:
                pass


def start_scheduler():
    """
    Starts the APScheduler background runner.
    """
    if not scheduler.running:
        scheduler.add_job(
            scheduled_rss_ingestion_job,
            "interval",
            minutes=30,
            id="rss_ingestion_job",
            replace_existing=True,
        )
        scheduler.start()
