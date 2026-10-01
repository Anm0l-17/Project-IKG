from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.source import Source
from app.services.ingestion.base import BaseIngestionAdapter
from app.services.ingestion.deduplication import (
    compute_article_hash,
    is_title_duplicate,
)


class IngestionPipeline:
    """
    Orchestrates source adapter execution, deduplication checks, and DB persistence.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_or_create_source(
        self, name: str, domain: str, rss_url: str | None = None
    ) -> Source:
        stmt = select(Source).where(Source.domain == domain)
        res = await self.db.execute(stmt)
        source = res.scalar_one_or_none()
        if not source:
            source = Source(
                name=name,
                domain=domain,
                rss_url=rss_url,
                trust_score=1.0,
                is_active=True,
            )
            self.db.add(source)
            await self.db.commit()
            await self.db.refresh(source)
        elif rss_url and source.rss_url != rss_url:
            source.rss_url = rss_url
            self.db.add(source)
            await self.db.commit()
            await self.db.refresh(source)
        return source

    async def ingest_from_adapter(
        self, adapter: BaseIngestionAdapter, limit: int = 50
    ) -> list[Article]:
        ingested_dtos = await adapter.fetch_articles(limit=limit)
        saved_articles: list[Article] = []

        if not ingested_dtos:
            return saved_articles

        source = await self._get_or_create_source(
            adapter.source_name, adapter.domain, getattr(adapter, "rss_url", None)
        )

        for dto in ingested_dtos:
            url_hash = compute_article_hash(dto.url)

            # O(1) Hash Deduplication Check
            existing_hash = await self.db.execute(
                select(Article).where(Article.hash == url_hash)
            )
            if existing_hash.scalar_one_or_none():
                continue

            # Title Fuzzy Match Check against recent articles (last 7 days, max 500)
            seven_days_ago = datetime.now(UTC) - timedelta(days=7)
            recent_articles_res = await self.db.execute(
                select(Article)
                .where(Article.created_at >= seven_days_ago)
                .order_by(Article.created_at.desc())
                .limit(500)
            )
            recent_articles = recent_articles_res.scalars().all()

            is_dup = False
            for recent in recent_articles:
                if is_title_duplicate(dto.headline, recent.headline, threshold=0.85):
                    is_dup = True
                    break

            if is_dup:
                continue

            # Store Article
            article = Article(
                source_id=source.id,
                url=dto.url,
                headline=dto.headline,
                author=dto.author,
                published_at=dto.published_at,
                scraped_at=datetime.now(UTC),
                raw_html_path=dto.raw_html,
                clean_text=dto.clean_text,
                summary=dto.summary,
                language=dto.language,
                hash=url_hash,
                status="FETCHED",
            )
            self.db.add(article)
            saved_articles.append(article)

        if saved_articles:
            await self.db.commit()
            for art in saved_articles:
                await self.db.refresh(art)

        return saved_articles
