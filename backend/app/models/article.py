from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Article(Base, TimestampMixin):
    """
    Represents an ingested news article.
    Articles serve exclusively as evidence attached to Events.
    """

    __tablename__ = "articles"

    source_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("sources.id"), nullable=False, index=True
    )
    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=True, index=True
    )

    url: Mapped[str] = mapped_column(
        String(512), unique=True, nullable=False, index=True
    )
    headline: Mapped[str] = mapped_column(String(512), nullable=False)
    author: Mapped[str] = mapped_column(String(255), nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    raw_html_path: Mapped[str] = mapped_column(String(255), nullable=True)
    clean_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    hash: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(
        String(20), default="FETCHED", nullable=False, index=True
    )
    # Statuses: FETCHED | NORMALISED | MATCHED | PENDING | VERIFIED | REJECTED

    # Relationships
    source: Mapped["Source"] = relationship("Source", back_populates="articles")
    event: Mapped["Event"] = relationship(
        "Event", back_populates="articles", foreign_keys=[event_id]
    )
