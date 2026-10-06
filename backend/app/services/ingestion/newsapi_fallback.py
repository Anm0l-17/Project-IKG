import logging
from datetime import UTC, datetime, timedelta

import dateutil.parser
import httpx

logger = logging.getLogger(__name__)
from app.services.ingestion.base import BaseIngestionAdapter, IngestedArticleDTO


class NewsAPIFallbackAdapter(BaseIngestionAdapter):
    """
    Secondary fallback adapter using NewsAPI aggregator service when primary RSS feeds are unreachable.
    """

    # Class-level state to persist backoff across scheduler instances
    _backoff_until: datetime | None = None

    def __init__(self, api_key: str | None = None):
        super().__init__(source_name="NewsAPI Aggregator", domain="newsapi.org")
        self.api_key = api_key

    async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
        articles: list[IngestedArticleDTO] = []
        if not self.api_key:
            return articles

        # Check if we are currently backing off due to rate limits
        if type(self)._backoff_until and datetime.now(UTC) < type(self)._backoff_until:
            logger.warning(
                f"NewsAPI adapter is backing off until {type(self)._backoff_until}"
            )
            return articles

        url = "https://newsapi.org/v2/top-headlines"
        params = {
            "country": "in",
            "category": "general",
            "pageSize": min(limit, 100),
            "apiKey": self.api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)

                if response.status_code == 429:
                    type(self)._backoff_until = datetime.now(UTC) + timedelta(hours=1)
                    logger.error(
                        "NewsAPI rate limit hit (429). Backing off for 1 hour."
                    )
                    return articles

                if response.status_code != 200:
                    return articles

                data = response.json()
                for item in data.get("articles", []):
                    headline = item.get("title", "")
                    link = item.get("url", "")
                    if not headline or not link:
                        continue

                    published_at = datetime.now(UTC)
                    if item.get("publishedAt"):
                        try:
                            published_at = dateutil.parser.parse(item["publishedAt"])
                            if published_at.tzinfo is None:
                                published_at = published_at.replace(tzinfo=UTC)
                        except (TypeError, ValueError, OverflowError) as error:
                            logger.warning("Failed to parse publishedAt date: %s", error)

                    clean_text = (
                        item.get("content") or item.get("description") or headline
                    )

                    articles.append(
                        IngestedArticleDTO(
                            source_name=item.get("source", {}).get(
                                "name", self.source_name
                            ),
                            source_domain=self.domain,
                            url=link,
                            headline=headline,
                            author=item.get("author"),
                            published_at=published_at,
                            clean_text=clean_text,
                            summary=item.get("description"),
                        )
                    )
        except (httpx.HTTPError, ValueError):
            logger.exception("NewsAPI fallback ingestion failed")

        return articles
