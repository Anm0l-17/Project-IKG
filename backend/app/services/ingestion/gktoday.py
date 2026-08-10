from datetime import datetime, timezone
import dateutil.parser
import feedparser
import httpx
from bs4 import BeautifulSoup
from app.services.ingestion.base import BaseIngestionAdapter, IngestedArticleDTO


class GKTodayAdapter(BaseIngestionAdapter):
    """
    Ingestion adapter for GKToday (Primary discovery source for Indian affairs).
    """
    def __init__(self, rss_url: str = "https://www.gktoday.in/feed/"):
        super().__init__(source_name="GKToday", domain="gktoday.in", rss_url=rss_url)

    async def fetch_articles(self, limit: int = 50) -> list[IngestedArticleDTO]:
        articles: list[IngestedArticleDTO] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                response = await client.get(self.rss_url)
                if response.status_code != 200:
                    return articles
                
                feed = feedparser.parse(response.text)
                for entry in feed.entries[:limit]:
                    title = getattr(entry, "title", "").strip()
                    link = getattr(entry, "link", "").strip()
                    if not title or not link:
                        continue

                    # Parse published date
                    published_at = datetime.now(timezone.utc)
                    if hasattr(entry, "published"):
                        try:
                            published_at = dateutil.parser.parse(entry.published)
                            if published_at.tzinfo is None:
                                published_at = published_at.replace(tzinfo=timezone.utc)
                        except Exception:
                            pass

                    # Clean summary/HTML content
                    summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
                    soup = BeautifulSoup(summary_raw, "html.parser")
                    clean_text = soup.get_text(separator=" ").strip() or title

                    articles.append(
                        IngestedArticleDTO(
                            source_name=self.source_name,
                            source_domain=self.domain,
                            url=link,
                            headline=title,
                            author=getattr(entry, "author", None),
                            published_at=published_at,
                            raw_html=summary_raw,
                            clean_text=clean_text,
                            summary=clean_text[:300] if len(clean_text) > 300 else clean_text
                        )
                    )
        except Exception:
            pass
            
        return articles
