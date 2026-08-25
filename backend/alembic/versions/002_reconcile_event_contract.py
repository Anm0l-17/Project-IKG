"""Reconcile Event status defaults, verifications, and Evidence contracts

Revision ID: 002_reconcile_event_contract
Revises: 001_initial_ontology_baseline
Create Date: 2026-08-25

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "002_reconcile_event_contract"
down_revision = "001_initial_ontology_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Update events server defaults for verification_status and status to canonical uppercase PENDING
    op.alter_column("events", "verification_status", server_default="PENDING")
    op.alter_column("events", "status", server_default="PENDING")
    op.alter_column("verifications", "status", server_default="PENDING")

    # 2. Normalize existing lowercase/mixed-case rows if any exist
    op.execute("UPDATE events SET verification_status = 'PENDING' WHERE verification_status = 'Pending';")
    op.execute("UPDATE events SET status = 'PENDING' WHERE status IN ('Pending', 'Candidate', 'Developing');")
    op.execute("UPDATE verifications SET status = 'PENDING' WHERE status = 'Pending';")

    # 3. Add index on evidence(event_id)
    op.create_index("ix_evidence_event_id", "evidence", ["event_id"])

    # 4. Backfill evidence for articles with event_id
    op.execute("""
        INSERT INTO evidence (id, article_id, event_id, evidence_type, confidence, reasoning, created_at, updated_at)
        SELECT 
            gen_random_uuid()::text,
            a.id,
            a.event_id,
            'EVENT_EXISTENCE',
            1.0,
            'Migrated from legacy articles.event_id foreign key shortcut',
            NOW(),
            NOW()
        FROM articles a
        WHERE a.event_id IS NOT NULL
        AND NOT EXISTS (
            SELECT 1 FROM evidence e WHERE e.article_id = a.id AND e.event_id = a.event_id
        );
    """)


def downgrade() -> None:
    op.drop_index("ix_evidence_event_id", table_name="evidence")
    op.alter_column("events", "verification_status", server_default="Pending")
    op.alter_column("events", "status", server_default="Candidate")
    op.alter_column("verifications", "status", server_default="Pending")
