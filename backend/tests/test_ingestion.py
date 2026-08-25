import pytest
from datetime import datetime, timezone, timedelta
from app.services.ingestion.base import BaseIngestionAdapter, IngestedArticleDTO
from app.services.ingestion.deduplication import compute_article_hash, is_title_duplicate, normalize_title
from app.services.ingestion.gktoday import GKTodayAdapter
from app.services.ingestion.thehindu import TheHinduAdapter
from app.services.ingestion.indianexpress import IndianExpressAdapter
from app.services.ingestion.newsapi_fallback import NewsAPIFallbackAdapter


def test_url_hash_computation():
    url1 = "https://www.gktoday.in/article-123#header"
    url2 = "https://www.gktoday.in/article-123/"
    assert compute_article_hash(url1) == compute_article_hash(url2)
    assert len(compute_article_hash(url1)) == 64


def test_title_deduplication_exact_and_fuzzy():
    title_a = "India signs historic trade agreement with UK in London"
    title_b = "India signs historic trade agreement with UK in London."
    title_c = "India signs historic trade agreement with UK"
    title_d = "RBI announces major interest rate cut today"

    assert is_title_duplicate(title_a, title_b, threshold=0.85) is True
    assert is_title_duplicate(title_a, title_c, threshold=0.80) is True
    assert is_title_duplicate(title_a, title_d, threshold=0.85) is False


def test_adapter_inheritance_and_dto():
    dto = IngestedArticleDTO(
        source_name="GKToday",
        source_domain="gktoday.in",
        url="https://gktoday.in/test",
        headline="Test Headline",
        clean_text="Test Clean Content"
    )
    assert dto.source_name == "GKToday"
    assert dto.headline == "Test Headline"

    gk_adapter = GKTodayAdapter()
    hindu_adapter = TheHinduAdapter()
    ie_adapter = IndianExpressAdapter()
    fallback_adapter = NewsAPIFallbackAdapter()

    assert isinstance(gk_adapter, BaseIngestionAdapter)
    assert isinstance(hindu_adapter, BaseIngestionAdapter)
    assert isinstance(ie_adapter, BaseIngestionAdapter)
    assert isinstance(fallback_adapter, BaseIngestionAdapter)


@pytest.mark.asyncio
async def test_fallback_cascade_logic():
    class FailingAdapter(BaseIngestionAdapter):
        async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
            return []

    class MockFallbackAdapter(BaseIngestionAdapter):
        async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
            return [
                IngestedArticleDTO(
                    source_name="FallbackSource",
                    source_domain="fallback.com",
                    url="https://fallback.com/article1",
                    headline="Fallback News Headline",
                    clean_text="Fallback content body"
                )
            ]

    failing = FailingAdapter(source_name="Failing", domain="failing.com")
    fallback = MockFallbackAdapter(source_name="Fallback", domain="fallback.com")

    articles = await failing.fetch_articles()
    if not articles:
        articles = await fallback.fetch_articles()

    assert len(articles) == 1
    assert articles[0].source_name == "FallbackSource"
    assert articles[0].headline == "Fallback News Headline"

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.source import Source
from app.models.article import Article
from app.services.ingestion.pipeline import IngestionPipeline

@pytest.mark.asyncio
async def test_pipeline_fuzzy_time_bound(db_session: AsyncSession):
    # Setup source and old article
    source = Source(name="Test", domain="test.com")
    db_session.add(source)
    await db_session.commit()

    old_article = Article(
        source_id=source.id,
        url="http://test.com/old",
        headline="Old News Headline",
        summary="Old summary",
        published_at=datetime.now(timezone.utc) - timedelta(days=10),
        scraped_at=datetime.now(timezone.utc) - timedelta(days=10),
        clean_text="Clean text",
        hash="oldhash"
    )
    db_session.add(old_article)
    await db_session.commit()
    
    # Manually override created_at to be older than 7 days
    old_article.created_at = datetime.now(timezone.utc) - timedelta(days=10)
    db_session.add(old_article)
    await db_session.commit()

    # Create mock adapter returning article with same headline
    class MockAdapter(BaseIngestionAdapter):
        async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
            return [
                IngestedArticleDTO(
                    source_name="Test",
                    source_domain="test.com",
                    url="http://test.com/new",
                    headline="Old News Headline", # Same title
                    clean_text="New content body"
                )
            ]

    pipeline = IngestionPipeline(db_session)
    saved = await pipeline.ingest_from_adapter(MockAdapter(source_name="Test", domain="test.com"))
    
    # Because old_article is >7 days old, it shouldn't be matched by the fuzzy duplicate check
    assert len(saved) == 1
    assert saved[0].url == "http://test.com/new"


def test_ingestion_scheduler_lifecycle():
    from app.workers.scheduler import IngestionScheduler
    scheduler = IngestionScheduler()
    scheduler.start(interval_minutes=60)
    assert scheduler.scheduler.running is True
    scheduler.shutdown()
    assert scheduler.scheduler.running is False

