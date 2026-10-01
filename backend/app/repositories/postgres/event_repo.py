from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.event import Event


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(
        self, event_id: str, load_timeline: bool = False
    ) -> Event | None:
        stmt = select(Event).where(Event.id == event_id)
        if load_timeline:
            stmt = stmt.options(selectinload(Event.timeline_entries))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Event | None:
        result = await self.session.execute(select(Event).where(Event.slug == slug))
        return result.scalar_one_or_none()

    async def get_feed_events(
        self,
        category: str | None = None,
        verification_status: str | None = "Verified",
        limit: int = 20,
    ) -> list[Event]:
        stmt = select(Event)
        if category:
            stmt = stmt.where(Event.category == category)
        if verification_status:
            stmt = stmt.where(Event.verification_status == verification_status)

        stmt = stmt.order_by(desc(Event.last_updated)).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_trending_events(self, limit: int = 10) -> list[Event]:
        stmt = (
            select(Event)
            .order_by(desc(Event.knowledge_score), desc(Event.last_updated))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_events(self, query: str, limit: int = 20) -> list[Event]:
        pattern = f"%{query}%"
        stmt = (
            select(Event)
            .where(Event.canonical_title.ilike(pattern) | Event.summary.ilike(pattern))
            .order_by(desc(Event.knowledge_score))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, event: Event) -> Event:
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        return event
