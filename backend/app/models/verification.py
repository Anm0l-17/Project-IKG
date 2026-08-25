from datetime import datetime
from sqlalchemy import String, Text, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.postgres import Base
from app.models.base import TimestampMixin


class Verification(Base, TimestampMixin):
    """
    Represents the verification consensus state for an Event.
    """
    __tablename__ = "verifications"

    event_id: Mapped[str] = mapped_column(String(36), ForeignKey("events.id"), unique=True, nullable=False, index=True)

    vote_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    required_votes: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False, index=True)
    # Status: PENDING | VERIFIED | REJECTED | ARCHIVED

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="verification")
    votes: Mapped[list["Vote"]] = relationship("Vote", back_populates="verification", cascade="all, delete-orphan")


class Vote(Base, TimestampMixin):
    """
    Represents a single publication's verification vote.
    Rules: 1 vote per publication per Event.
    """
    __tablename__ = "votes"

    verification_id: Mapped[str] = mapped_column(String(36), ForeignKey("verifications.id"), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id"), nullable=False, index=True)
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("articles.id"), nullable=False, index=True)

    decision: Mapped[str] = mapped_column(String(20), nullable=False) # MATCHED | SAME_EVENT | FOLLOW_UP
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    verification: Mapped["Verification"] = relationship("Verification", back_populates="votes")
