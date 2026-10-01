from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Topic(Base, TimestampMixin):
    """
    Reusable subject area within a Domain.
    Example: Domain (Trade) -> Topic (India-UK Trade Relations).
    """

    __tablename__ = "topics"

    domain_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("domains.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    slug: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="ACTIVE", nullable=False, index=True
    )
    # Status: ACTIVE | INACTIVE

    # Relationships
    domain: Mapped["Domain"] = relationship("Domain", back_populates="topics")
    stories: Mapped[list["Story"]] = relationship(
        "Story", back_populates="topic", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="topic")
