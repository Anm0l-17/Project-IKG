from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.db.types import VectorType
from app.models.base import TimestampMixin


class Event(Base, TimestampMixin):
    """
    Primary Knowledge Object.
    Events represent real-world occurrences, owned by timelines, verifications, and entities.
    """

    __tablename__ = "events"

    canonical_title: Mapped[str] = mapped_column(String(512), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False, index=True
    )

    domain_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("domains.id"), nullable=True, index=True
    )
    topic_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("topics.id"), nullable=True, index=True
    )
    primary_story_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stories.id"), nullable=True, index=True
    )
    canonical_article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id"), nullable=True, index=True
    )

    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Categories: Current Affairs | Parliament | Economics | Trade | Defence | Geopolitics
    subcategory: Mapped[str] = mapped_column(String(100), nullable=True)

    summary: Mapped[str] = mapped_column(Text, nullable=True)
    knowledge_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, index=True
    )
    importance_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(
        VectorType(384), nullable=True
    )

    grouping_status: Mapped[str] = mapped_column(
        String(20), default="UNGROUPED", nullable=False, index=True
    )
    # Grouping Status: UNGROUPED | GROUPED

    verification_status: Mapped[str] = mapped_column(
        String(20), default="PENDING", nullable=False, index=True
    )
    # Verification Statuses: PENDING | VERIFIED | REJECTED | ARCHIVED

    status: Mapped[str] = mapped_column(
        String(20), default="PENDING", nullable=False, index=True
    )
    # States: DISCOVERED | NORMALISED | MATCHING | PENDING | VERIFIED | ACTIVE | HISTORICAL | ARCHIVED | DEPRECATED

    first_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

    # Relationships
    domain: Mapped["Domain"] = relationship("Domain", back_populates="events")
    topic: Mapped["Topic"] = relationship("Topic", back_populates="events")
    primary_story: Mapped["Story"] = relationship(
        "Story", back_populates="events", foreign_keys=[primary_story_id]
    )
    canonical_article: Mapped["Article"] = relationship(
        "Article", foreign_keys=[canonical_article_id]
    )

    articles: Mapped[list["Article"]] = relationship(
        "Article", back_populates="event", foreign_keys="[Article.event_id]"
    )
    claims: Mapped[list["Claim"]] = relationship(
        "Claim", back_populates="event", cascade="all, delete-orphan"
    )
    evidence_items: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="event", cascade="all, delete-orphan"
    )
    timeline_entries: Mapped[list["TimelineEntry"]] = relationship(
        "TimelineEntry", back_populates="event", cascade="all, delete-orphan"
    )
    verification: Mapped["Verification"] = relationship(
        "Verification",
        back_populates="event",
        uselist=False,
        cascade="all, delete-orphan",
    )
    event_entities: Mapped[list["EventEntity"]] = relationship(
        "EventEntity", back_populates="event", cascade="all, delete-orphan"
    )
    outgoing_relationships: Mapped[list["EventRelationship"]] = relationship(
        "EventRelationship",
        foreign_keys="[EventRelationship.source_event_id]",
        back_populates="source_event",
        cascade="all, delete-orphan",
    )
    incoming_relationships: Mapped[list["EventRelationship"]] = relationship(
        "EventRelationship",
        foreign_keys="[EventRelationship.target_event_id]",
        back_populates="target_event",
        cascade="all, delete-orphan",
    )
