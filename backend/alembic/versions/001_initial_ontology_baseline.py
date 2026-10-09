"""Initial Ontology Baseline with pgvector support

Revision ID: 001_initial_ontology_baseline
Revises:
Create Date: 2026-08-10

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial_ontology_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Create pgvector extension if available
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Domains Table
    op.create_table(
        "domains",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), unique=True, nullable=False),
        sa.Column("slug", sa.String(length=100), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_domains_id", "domains", ["id"])
    op.create_index("ix_domains_name", "domains", ["name"])
    op.create_index("ix_domains_slug", "domains", ["slug"])

    # 3. Topics Table
    op.create_table(
        "topics",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("domain_id", sa.String(length=36), sa.ForeignKey("domains.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("slug", sa.String(length=255), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="ACTIVE", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_topics_id", "topics", ["id"])
    op.create_index("ix_topics_domain_id", "topics", ["domain_id"])
    op.create_index("ix_topics_slug", "topics", ["slug"])

    # 4. Stories Table
    op.create_table(
        "stories",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("topic_id", sa.String(length=36), sa.ForeignKey("topics.id"), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("slug", sa.String(length=512), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="PENDING", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_stories_id", "stories", ["id"])
    op.create_index("ix_stories_topic_id", "stories", ["topic_id"])
    op.create_index("ix_stories_slug", "stories", ["slug"])

    # 5. Sources Table
    op.create_table(
        "sources",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("domain", sa.String(length=100), unique=True, nullable=False),
        sa.Column("rss_url", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("country", sa.String(length=10), server_default="IN", nullable=False),
        sa.Column("trust_score", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sources_id", "sources", ["id"])
    op.create_index("ix_sources_domain", "sources", ["domain"])

    # 6. Articles Table
    op.create_table(
        "articles",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("source_id", sa.String(length=36), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("event_id", sa.String(length=36), nullable=True),
        sa.Column("url", sa.String(length=512), unique=True, nullable=False),
        sa.Column("headline", sa.String(length=512), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("scraped_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("raw_html_path", sa.String(length=255), nullable=True),
        sa.Column("clean_text", sa.Text(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("language", sa.String(length=10), server_default="en", nullable=False),
        sa.Column("hash", sa.String(length=64), unique=True, nullable=False),
        sa.Column("status", sa.String(length=20), server_default="FETCHED", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_articles_id", "articles", ["id"])
    op.create_index("ix_articles_source_id", "articles", ["source_id"])
    op.create_index("ix_articles_url", "articles", ["url"])
    op.create_index("ix_articles_hash", "articles", ["hash"])

    # 7. Events Table
    op.create_table(
        "events",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("canonical_title", sa.String(length=512), nullable=False),
        sa.Column("slug", sa.String(length=512), unique=True, nullable=False),
        sa.Column("domain_id", sa.String(length=36), sa.ForeignKey("domains.id"), nullable=True),
        sa.Column("topic_id", sa.String(length=36), sa.ForeignKey("topics.id"), nullable=True),
        sa.Column("primary_story_id", sa.String(length=36), sa.ForeignKey("stories.id"), nullable=True),
        sa.Column("canonical_article_id", sa.String(length=36), sa.ForeignKey("articles.id"), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subcategory", sa.String(length=100), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("knowledge_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("importance_score", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("grouping_status", sa.String(length=20), server_default="UNGROUPED", nullable=False),
        sa.Column("verification_status", sa.String(length=20), server_default="Pending", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="Candidate", nullable=False),
        sa.Column("first_seen", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_events_id", "events", ["id"])
    op.create_index("ix_events_slug", "events", ["slug"])
    op.create_index("ix_events_category", "events", ["category"])
    op.create_index("ix_events_grouping_status", "events", ["grouping_status"])
    op.create_index("ix_events_verification_status", "events", ["verification_status"])

    # Foreign Key from Articles back to Events
    op.create_foreign_key("fk_articles_event_id", "articles", "events", ["event_id"], ["id"])

    # 8. Claims Table
    op.create_table(
        "claims",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("article_id", sa.String(length=36), sa.ForeignKey("articles.id"), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_claims_id", "claims", ["id"])
    op.create_index("ix_claims_event_id", "claims", ["event_id"])
    op.create_index("ix_claims_article_id", "claims", ["article_id"])

    # 9. Evidence Table
    op.create_table(
        "evidence",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("article_id", sa.String(length=36), sa.ForeignKey("articles.id"), nullable=False),
        sa.Column("claim_id", sa.String(length=36), sa.ForeignKey("claims.id"), nullable=True),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=True),
        sa.Column("evidence_type", sa.String(length=50), nullable=False),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_id", "evidence", ["id"])
    op.create_index("ix_evidence_article_id", "evidence", ["article_id"])

    # 10. Entities Table
    op.create_table(
        "entities",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("canonical_name", sa.String(length=255), unique=True, nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("aliases", sa.JSON(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("importance", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_entities_id", "entities", ["id"])
    op.create_index("ix_entities_canonical_name", "entities", ["canonical_name"])

    # 11. Event Entities Link Table
    op.create_table(
        "event_entities",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("entity_id", sa.String(length=36), sa.ForeignKey("entities.id"), nullable=False),
        sa.Column("relationship_type", sa.String(length=100), server_default="MENTIONS", nullable=False),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_event_entities_id", "event_entities", ["id"])

    # 12. Timeline Entries Table
    op.create_table(
        "timeline_entries",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("importance", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("source_count", sa.Integer(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_timeline_entries_id", "timeline_entries", ["id"])

    # 13. Verifications Table
    op.create_table(
        "verifications",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("event_id", sa.String(length=36), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("vote_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("required_votes", sa.Integer(), server_default="2", nullable=False),
        sa.Column("confidence", sa.Float(), server_default="0.0", nullable=False),
        sa.Column("status", sa.String(length=20), server_default="Pending", nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # 14. Votes Table
    op.create_table(
        "votes",
        sa.Column("id", sa.String(length=36), primary_key=True, nullable=False),
        sa.Column("verification_id", sa.String(length=36), sa.ForeignKey("verifications.id"), nullable=False),
        sa.Column("source_id", sa.String(length=36), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("article_id", sa.String(length=36), sa.ForeignKey("articles.id"), nullable=False),
        sa.Column("decision", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("confidence", sa.Float(), server_default="1.0", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("votes")
    op.drop_table("verifications")
    op.drop_table("timeline_entries")
    op.drop_table("event_entities")
    op.drop_table("entities")
    op.drop_table("evidence")
    op.drop_table("claims")
    op.drop_constraint("fk_articles_event_id", "articles", type_="foreignkey")
    op.drop_table("events")
    op.drop_table("articles")
    op.drop_table("sources")
    op.drop_table("stories")
    op.drop_table("topics")
    op.drop_table("domains")
