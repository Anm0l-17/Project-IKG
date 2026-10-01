import time
import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column


def generate_uuid7() -> str:
    """
    Generates a UUID v7 string (chronologically sortable, globally unique).
    UUID v7 layout: 48-bit timestamp + 74-bit random/sequence data.
    """
    timestamp_ms = int(time.time() * 1000)
    rand_a = uuid.uuid4().int & 0xFFF
    rand_b = uuid.uuid4().int & 0x3FFFFFFFFFFFFFFF

    uuid_int = (
        (timestamp_ms << 80)
        | (0x7 << 76)
        | (rand_a << 64)
        | (0b10 << 62)
        | rand_b
    )
    return str(uuid.UUID(int=uuid_int))


class TimestampMixin:
    """Mixin for UUID v7 Primary Key and created_at / updated_at timestamps."""

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=generate_uuid7, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )
