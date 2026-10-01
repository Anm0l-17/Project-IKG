from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Story(Base, TimestampMixin):
    """
    Long-running, bounded narrative within a Topic.
    Example: Topic (India-UK Trade Relations) -> Story (India-UK FTA 2026).
    Requires at least two qualifying Events with independent sources.
    """

    __tablename__ = "stories"

    topic_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topics.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    status: Mapped[str] = mapped_column(
        String(20), default="PENDING", nullable=False, index=True
    )
    # Lifecycle: PENDING -> VERIFIED -> ARCHIVED (or REJECTED)

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="stories")
    events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="primary_story", foreign_keys="[Event.primary_story_id]"
    )
