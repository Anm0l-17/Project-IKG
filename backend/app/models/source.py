from sqlalchemy import Boolean, Float, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Source(Base, TimestampMixin):
    """
    Represents a trusted publication source.
    Version 1 trusted sources: GKToday (discovery), The Hindu, The Indian Express (verification).
    """

    __tablename__ = "sources"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    domain: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    rss_url: Mapped[str] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    country: Mapped[str] = mapped_column(String(10), default="IN", nullable=False)
    trust_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    logo_url: Mapped[str] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    articles: Mapped[list["Article"]] = relationship(
        "Article", back_populates="source", cascade="all, delete-orphan"
    )
