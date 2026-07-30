from datetime import datetime, timezone
from sqlalchemy import String, Text, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.postgres import Base
from app.models.base import TimestampMixin


class Event(Base, TimestampMixin):
    """
    Primary Knowledge Object.
    Events represent real-world occurrences, owned by timelines, verifications, and entities.
    """
    __tablename__ = "events"

    canonical_title: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(String(512), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: Current Affairs | Parliament | Economics | Trade | Defence | Geopolitics
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True)

    summary: Mapped[str] = mapped_column(Text, nullable=True)
    knowledge_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False, index=True)
    importance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    verification_status: Mapped[str] = mapped_column(String(20), default="Pending", nullable=False, index=True)
    # Verification Statuses: Pending | Verified | Rejected | Expired | Archived

    status: Mapped[str] = mapped_column(String(20), default="Candidate", nullable=False, index=True)
    # States: Candidate | Discovered | Matching | Pending | Verified | Active | Historical | Archived | Deprecated

    first_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    articles: Mapped[list["Article"]] = relationship("Article", back_populates="event")
    timeline_entries: Mapped[list["TimelineEntry"]] = relationship("TimelineEntry", back_populates="event", cascade="all, delete-orphan")
    verification: Mapped["Verification"] = relationship("Verification", back_populates="event", uselist=False, cascade="all, delete-orphan")
    event_entities: Mapped[list["EventEntity"]] = relationship("EventEntity", back_populates="event", cascade="all, delete-orphan")
