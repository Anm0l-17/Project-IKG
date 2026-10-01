from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class EventRelationship(Base, TimestampMixin):
    """
    Directional, confidence-bearing edge connecting two Events in the Knowledge Graph.
    Inferred via deterministic rules (PRECEDES, CAUSES, RELATED_TO, etc.) or AI suggestions.
    """

    __tablename__ = "event_relationships"

    source_event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=False, index=True
    )
    target_event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=False, index=True
    )

    relationship_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )
    # Types: PRECEDES | CAUSES | RELATED_TO | FOLLOWS | SUPPORTS | OPPOSES | REPLACES

    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), default="VALIDATED", nullable=False, index=True
    )
    # Status: VALIDATED | PROPOSED | REJECTED

    reasoning: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    source_event: Mapped["Event"] = relationship(
        "Event", foreign_keys=[source_event_id], back_populates="outgoing_relationships"
    )
    target_event: Mapped["Event"] = relationship(
        "Event", foreign_keys=[target_event_id], back_populates="incoming_relationships"
    )
