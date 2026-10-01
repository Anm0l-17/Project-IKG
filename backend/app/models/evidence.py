from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Evidence(Base, TimestampMixin):
    """
    Explicitly connects an Article or Claim to an Event, Story grouping, or Relationship.
    """

    __tablename__ = "evidence"

    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id"), nullable=False, index=True
    )
    claim_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("claims.id"), nullable=True, index=True
    )
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=True, index=True
    )

    evidence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    # Types: EVENT_EXISTENCE | STORY_GROUPING | RELATIONSHIP_SUPPORT | CLAIM_PROVENANCE
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    article: Mapped["Article"] = relationship("Article")
    claim: Mapped["Claim"] = relationship("Claim", back_populates="evidence_links")
    event: Mapped["Event"] = relationship("Event", back_populates="evidence_items")
