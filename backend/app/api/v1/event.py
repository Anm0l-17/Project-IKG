from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.repositories.postgres.event_repo import EventRepository
from app.schemas.event import EventDetailResponse

router = APIRouter()


@router.get("/events/{id}", response_model=EventDetailResponse)
async def get_event(
    id: str,
    db: AsyncSession = Depends(get_db)
):
    repo = EventRepository(db)
    event = await repo.get_by_id(id, load_timeline=True)

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested event does not exist."
        )

    return EventDetailResponse.model_validate(event)
