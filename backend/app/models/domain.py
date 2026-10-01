from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin


class Domain(Base, TimestampMixin):
    """
    Fixed top-level taxonomy object.
    V1 Domains: Current Affairs, Parliament, Economics, Trade, Defence, Geopolitics.
    """

    __tablename__ = "domains"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Relationships
    topics: Mapped[list["Topic"]] = relationship(
        "Topic", back_populates="domain", cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="domain")
