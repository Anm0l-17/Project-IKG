from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class IngestedArticleDTO(BaseModel):
    """
    Data Transfer Object for parsed raw articles before database persistence.
    """
    source_name: str
    source_domain: str
    url: str
    headline: str
    author: Optional[str] = None
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_html: Optional[str] = None
    clean_text: str
    summary: Optional[str] = None
    language: str = "en"


class BaseIngestionAdapter(ABC):
    """
    Abstract base adapter for all source ingestion providers.
    Decouples source-specific parsing logic from the core pipeline.
    """
    def __init__(self, source_name: str, domain: str, rss_url: Optional[str] = None):
        self.source_name = source_name
        self.domain = domain
        self.rss_url = rss_url

    @abstractmethod
    async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
        """
        Fetches and normalizes articles from the publisher.
        Must return a list of IngestedArticleDTO instances.
        """
        pass
