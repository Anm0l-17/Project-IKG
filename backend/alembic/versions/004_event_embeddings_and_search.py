"""Add event embedding column and search indices for Semantic and Hybrid Search

Revision ID: 004_event_embeddings_and_search
Revises: 003_event_relationships
Create Date: 2026-09-25

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "004_event_embeddings_and_search"
down_revision = "003_event_relationships"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Add embedding column to events
    op.add_column("events", sa.Column("embedding", sa.JSON(), nullable=True))

    # 2. If running on PostgreSQL with pgvector, attempt creating HNSW index
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        # Create HNSW index for cosine distance if vector cast is supported
        try:
            op.execute("""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
                        -- Create functional HNSW index on events vector representation if possible
                        EXECUTE 'CREATE INDEX IF NOT EXISTS ix_events_embedding_hnsw ON events USING hnsw ((embedding::text::vector(384)) vector_cosine_ops) WITH (m = 16, ef_construction = 64);';
                    END IF;
                EXCEPTION WHEN OTHERS THEN
                    RAISE NOTICE 'Skipping HNSW index creation: %', SQLERRM;
                END $$;
            """)
        except sa.exc.DBAPIError:
            pass

        # Create GIN full text search index for lexical retrieval
        try:
            op.execute("""
                CREATE INDEX IF NOT EXISTS ix_events_fts ON events 
                USING gin(to_tsvector('english', coalesce(canonical_title, '') || ' ' || coalesce(summary, '')));
            """)
        except sa.exc.DBAPIError:
            pass


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name
    if dialect == "postgresql":
        try:
            op.execute("DROP INDEX IF EXISTS ix_events_fts;")
            op.execute("DROP INDEX IF EXISTS ix_events_embedding_hnsw;")
        except sa.exc.DBAPIError:
            pass

    op.drop_column("events", "embedding")
