from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.repositories.postgres.event_repo import EventRepository
from app.repositories.postgres.timeline_repo import TimelineRepository
from app.schemas.timeline import TimelineEntryResponse

router = APIRouter()


@router.get("/events/{id}/timeline", response_model=list[TimelineEntryResponse])
async def get_event_timeline(id: str, db: AsyncSession = Depends(get_db)):
    event_repo = EventRepository(db)
    event = await event_repo.get_by_id(id)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested event does not exist.",
        )

    timeline_repo = TimelineRepository(db)
    entries = await timeline_repo.get_by_event_id(id)

    return [TimelineEntryResponse.model_validate(e) for e in entries]
