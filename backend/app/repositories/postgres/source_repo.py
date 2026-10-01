from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source


class SourceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, source_id: str) -> Source | None:
        result = await self.session.execute(
            select(Source).where(Source.id == source_id)
        )
        return result.scalar_one_or_none()

    async def get_by_domain(self, domain: str) -> Source | None:
        result = await self.session.execute(
            select(Source).where(Source.domain == domain)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> list[Source]:
        result = await self.session.execute(
            select(Source).where(Source.is_active == True)
        )
        return list(result.scalars().all())

    async def create(self, source: Source) -> Source:
        self.session.add(source)
        await self.session.commit()
        await self.session.refresh(source)
        return source
