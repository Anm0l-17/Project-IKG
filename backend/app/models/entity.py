from typing import TYPE_CHECKING

from sqlalchemy import JSON, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.postgres import Base
from app.models.base import TimestampMixin

if TYPE_CHECKING:
    from app.models.event import Event


class Entity(Base, TimestampMixin):
    """
    Represents a reusable NER entity (Country, Ministry, Policy, Person, Company, etc.)
    """

    __tablename__ = "entities"

    canonical_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Types: Country | State | City | Person | Company | Policy | Act | Bill | Organisation | Committee | Ministry | Scheme | Court

    aliases: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    importance: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    event_entities: Mapped[list["EventEntity"]] = relationship(
        "EventEntity", back_populates="entity"
    )


class EventEntity(Base, TimestampMixin):
    """
    Many-to-many link table between Events and Entities.
    """

    __tablename__ = "event_entities"

    event_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("events.id"), nullable=False, index=True
    )
    entity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("entities.id"), nullable=False, index=True
    )

    relationship_type: Mapped[str] = mapped_column(
        String(100), default="MENTIONS", nullable=False
    )
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    # Relationships
    event: Mapped["Event"] = relationship("Event", back_populates="event_entities")
    entity: Mapped["Entity"] = relationship("Entity", back_populates="event_entities")
