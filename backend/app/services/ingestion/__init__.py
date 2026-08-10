from app.services.ingestion.base import BaseIngestionAdapter, IngestedArticleDTO
from app.services.ingestion.gktoday import GKTodayAdapter
from app.services.ingestion.thehindu import TheHinduAdapter
from app.services.ingestion.indianexpress import IndianExpressAdapter
from app.services.ingestion.newsapi_fallback import NewsAPIFallbackAdapter
from app.services.ingestion.pipeline import IngestionPipeline
from app.services.ingestion.deduplication import compute_article_hash, is_title_duplicate

__all__ = [
    "BaseIngestionAdapter",
    "IngestedArticleDTO",
    "GKTodayAdapter",
    "TheHinduAdapter",
    "IndianExpressAdapter",
    "NewsAPIFallbackAdapter",
    "IngestionPipeline",
    "compute_article_hash",
    "is_title_duplicate",
]
