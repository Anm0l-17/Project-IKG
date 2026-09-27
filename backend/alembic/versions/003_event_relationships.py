"""Add event_relationships table for Knowledge Graph edges

Revision ID: 003_event_relationships
Revises: 002_reconcile_event_contract
Create Date: 2026-09-20

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "003_event_relationships"
down_revision = "002_reconcile_event_contract"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "event_relationships",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("source_event_id", sa.String(length=36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_event_id", sa.String(length=36), sa.ForeignKey("events.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relationship_type", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("evidence_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="VALIDATED", nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_event_relationships_id", "event_relationships", ["id"])
    op.create_index("ix_event_relationships_source_event_id", "event_relationships", ["source_event_id"])
    op.create_index("ix_event_relationships_target_event_id", "event_relationships", ["target_event_id"])
    op.create_index("ix_event_relationships_relationship_type", "event_relationships", ["relationship_type"])
    op.create_index("ix_event_relationships_status", "event_relationships", ["status"])


def downgrade() -> None:
    op.drop_index("ix_event_relationships_status", table_name="event_relationships")
    op.drop_index("ix_event_relationships_relationship_type", table_name="event_relationships")
    op.drop_index("ix_event_relationships_target_event_id", table_name="event_relationships")
    op.drop_index("ix_event_relationships_source_event_id", table_name="event_relationships")
    op.drop_index("ix_event_relationships_id", table_name="event_relationships")
    op.drop_table("event_relationships")
