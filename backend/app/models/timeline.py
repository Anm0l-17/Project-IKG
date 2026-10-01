from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class TimelineEntry(Base, TimestampMixin):
    """
    Represents an entry in an Event's chronological evolution timeline.
    """

    __tablename__ = "timeline_entries"

    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=False, index=True
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)

    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    importance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    source_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="timeline_entries")
