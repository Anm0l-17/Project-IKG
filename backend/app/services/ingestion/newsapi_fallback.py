from datetime import datetime, timezone
import dateutil.parser
import httpx
from typing import Optional
from app.services.ingestion.base import BaseIngestionAdapter, IngestedArticleDTO


class NewsAPIFallbackAdapter(BaseIngestionAdapter):
    """
    Secondary fallback adapter using NewsAPI aggregator service when primary RSS feeds are unreachable.
    """
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(source_name="NewsAPI Aggregator", domain="newsapi.org")
        self.api_key = api_key

    async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
        articles: list[IngestedArticleDTO] = []
        if not self.api_key:
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
                if response.status_code != 200:
                    return articles

                data = response.json()
                for item in data.get("articles", []):
                    headline = item.get("title", "")
                    link = item.get("url", "")
                    if not headline or not link:
                        continue

                    published_at = datetime.now(timezone.utc)
                    if item.get("publishedAt"):
                        try:
                            published_at = dateutil.parser.parse(item["publishedAt"])
                            if published_at.tzinfo is None:
                                published_at = published_at.replace(tzinfo=timezone.utc)
                        except Exception:
                            pass

                    clean_text = item.get("content") or item.get("description") or headline

                    articles.append(
                        IngestedArticleDTO(
                            source_name=item.get("source", {}).get("name", self.source_name),
                            source_domain=self.domain,
                            url=link,
                            headline=headline,
                            author=item.get("author"),
                            published_at=published_at,
                            clean_text=clean_text,
                            summary=item.get("description")
                        )
                    )
        except Exception:
            pass

        return articles
