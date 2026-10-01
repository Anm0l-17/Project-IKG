from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Claim(Base, TimestampMixin):
    """
    Article-specific assertion extracted from an Article.
    Each Claim belongs to exactly one Event.
    """

    __tablename__ = "claims"

    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=False, index=True
    )
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id"), nullable=False, index=True
    )

    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="claims")
    article: Mapped["Article"] = relationship("Article")
    evidence_links: Mapped[list["Evidence"]] = relationship(
        "Evidence", back_populates="claim"
    )
