from sqlalchemy import asc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.timeline import TimelineEntry


class TimelineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_event_id(self, event_id: str) -> list[TimelineEntry]:
        stmt = (
            select(TimelineEntry)
            .where(TimelineEntry.event_id == event_id)
            .order_by(asc(TimelineEntry.sequence))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, entry: TimelineEntry) -> TimelineEntry:
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry
