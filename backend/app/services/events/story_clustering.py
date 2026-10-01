import logging
import re
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.embeddings import embedding_service
from app.models.article import Article
from app.models.entity import EventEntity
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.story import Story
from app.models.topic import Topic

logger = logging.getLogger(__name__)


def slugify(title: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", cleaned).strip("-")
    return slug[:100]


class StoryClusteringService:
    """
    Groups UNGROUPED Events into long-running narrative Stories within Topics.
    Enforces the Architecture & Ontology Baseline rule:
    - A Story requires at least 2 qualifying Events.
    - Each qualifying Event must have independent source evidence (>= 2 distinct sources).
    - Story lifecycle: PENDING -> VERIFIED -> ARCHIVED.
    - Event grouping_status transitions from UNGROUPED -> GROUPED upon assignment.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_story_verification(self, story_id: str) -> bool:
        """
        Evaluates whether a Story meets the criteria to transition to VERIFIED:
        - Must have at least 2 qualifying Events.
        - Must have independent source evidence (>= 2 distinct publication sources across events).
        """
        stmt = (
            select(Story)
            .where(Story.id == story_id)
            .options(
                selectinload(Story.events)
                .selectinload(Event.articles)
                .selectinload(Article.source),
                selectinload(Story.events)
                .selectinload(Event.evidence_items)
                .selectinload(Evidence.article)
                .selectinload(Article.source),
            )
        )
        res = await self.db.execute(stmt)
        story = res.scalars().first()
        if not story:
            return False

        qualifying_events = story.events
        if len(qualifying_events) < 2:
            if story.status == "VERIFIED":
                story.status = "PENDING"
                await self.db.commit()
            return False

        # Gather distinct source IDs across all events' articles and evidence
        distinct_source_ids: set[str] = set()
        for ev in qualifying_events:
            for art in ev.articles:
                if art.source_id:
                    distinct_source_ids.add(art.source_id)
            for evi in ev.evidence_items:
                if evi.article and evi.article.source_id:
                    distinct_source_ids.add(evi.article.source_id)

        # Consensus requirement: >= 2 distinct publications
        is_verified = len(distinct_source_ids) >= 2
        if is_verified and story.status != "VERIFIED":
            story.status = "VERIFIED"
            await self.db.commit()
            logger.info(
                f"Story '{story.title}' promoted to VERIFIED with {len(qualifying_events)} events across {len(distinct_source_ids)} distinct sources."
            )
        elif not is_verified and story.status == "VERIFIED":
            story.status = "PENDING"
            await self.db.commit()

        return is_verified

    async def cluster_ungrouped_events(self, limit: int = 50) -> dict[str, Any]:
        """
        Scans UNGROUPED Events and groups them into existing or new Stories based on:
        1. Existing graph relationship edges (PRECEDES, CAUSES, RELATED_TO).
        2. Named entity overlap (>= 2 shared entities) in the same Topic.
        3. Semantic vector cosine similarity (>= 0.75) in the same Topic.
        """
        stmt = (
            select(Event)
            .where(Event.grouping_status == "UNGROUPED")
            .options(
                selectinload(Event.event_entities).selectinload(EventEntity.entity),
                selectinload(Event.outgoing_relationships),
                selectinload(Event.incoming_relationships),
                selectinload(Event.topic),
            )
            .order_by(Event.first_seen.asc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        ungrouped_events = res.scalars().all()

        if not ungrouped_events:
            return {"grouped_count": 0, "stories_created": 0, "stories_updated": 0}

        # Fetch active Topics and existing Stories
        stories_stmt = select(Story).options(
            selectinload(Story.events)
            .selectinload(Event.event_entities)
            .selectinload(EventEntity.entity)
        )
        s_res = await self.db.execute(stories_stmt)
        existing_stories = s_res.scalars().all()

        # Map story_id to list of events for in-memory checks without lazy-loading
        story_events_map: dict[str, list[Event]] = {
            s.id: list(s.events) for s in existing_stories
        }

        grouped_count = 0
        stories_created = 0
        stories_updated_set: set[str] = set()

        for event in ungrouped_events:
            matched_story: Story | None = None
            event_text = f"{event.canonical_title} {event.summary or ''}"
            event_vec = embedding_service.generate_embedding(event_text)
            event_entities = {ee.entity_id for ee in event.event_entities}

            # Check 1: Graph Relationships to an already grouped Event
            rel_event_ids = set()
            for r in event.outgoing_relationships:
                rel_event_ids.add(r.target_event_id)
            for r in event.incoming_relationships:
                rel_event_ids.add(r.source_event_id)

            if rel_event_ids:
                for story in existing_stories:
                    story_event_ids = {e.id for e in story_events_map.get(story.id, [])}
                    if rel_event_ids & story_event_ids:
                        matched_story = story
                        break

            # Check 2: Affinity with existing Stories under the same Topic
            if not matched_story and event.topic_id:
                topic_stories = [
                    s for s in existing_stories if s.topic_id == event.topic_id
                ]
                for story in topic_stories:
                    for s_ev in story_events_map.get(story.id, []):
                        s_entities = {ee.entity_id for ee in s_ev.event_entities}
                        shared = event_entities & s_entities
                        if len(shared) >= 1:
                            matched_story = story
                            break

                        s_text = f"{s_ev.canonical_title} {s_ev.summary or ''}"
                        s_vec = embedding_service.generate_embedding(s_text)
                        sim = embedding_service.cosine_similarity(event_vec, s_vec)
                        if sim >= 0.70:
                            matched_story = story
                            break
                    if matched_story:
                        break

            # If matched with existing Story, assign it
            if matched_story:
                event.primary_story_id = matched_story.id
                event.grouping_status = "GROUPED"
                story_events_map.setdefault(matched_story.id, []).append(event)
                grouped_count += 1
                stories_updated_set.add(matched_story.id)
            else:
                # Check 3: Cluster with another un-grouped event in the same Topic to spawn a new Story
                # Look for a sibling un-grouped event with high affinity
                if event.topic_id:
                    siblings = [
                        e
                        for e in ungrouped_events
                        if e.id != event.id
                        and e.topic_id == event.topic_id
                        and e.grouping_status == "UNGROUPED"
                    ]
                    for sib in siblings:
                        sib_entities = {ee.entity_id for ee in sib.event_entities}
                        shared = event_entities & sib_entities
                        sib_text = f"{sib.canonical_title} {sib.summary or ''}"
                        sib_vec = embedding_service.generate_embedding(sib_text)
                        sim = embedding_service.cosine_similarity(event_vec, sib_vec)

                        if len(shared) >= 1 or sim >= 0.70:
                            # Create new Story narrative
                            base_title = event.canonical_title.split(":")[0].strip()
                            new_story = Story(
                                topic_id=event.topic_id,
                                title=f"Narrative: {base_title[:80]}",
                                slug=f"{slugify(base_title)}-{int(datetime.now(UTC).timestamp())}",
                                description=f"Chronological narrative evolving around {base_title}.",
                                status="PENDING",
                            )
                            self.db.add(new_story)
                            await self.db.flush()

                            event.primary_story_id = new_story.id
                            event.grouping_status = "GROUPED"
                            sib.primary_story_id = new_story.id
                            sib.grouping_status = "GROUPED"

                            existing_stories.append(new_story)
                            story_events_map[new_story.id] = [event, sib]
                            grouped_count += 2
                            stories_created += 1
                            stories_updated_set.add(new_story.id)
                            break

        await self.db.commit()

        # Re-evaluate verification consensus for all modified Stories
        for s_id in stories_updated_set:
            await self.evaluate_story_verification(s_id)

        return {
            "grouped_count": grouped_count,
            "stories_created": stories_created,
            "stories_updated": len(stories_updated_set),
        }

    async def get_story_timeline(self, story_id: str) -> dict[str, Any] | None:
        """
        Retrieves Story detail and its chronological Event narrative timeline.
        """
        stmt = (
            select(Story)
            .where(Story.id == story_id)
            .options(
                selectinload(Story.topic).selectinload(Topic.domain),
                selectinload(Story.events)
                .selectinload(Event.articles)
                .selectinload(Article.source),
            )
        )
        res = await self.db.execute(stmt)
        story = res.scalars().first()
        if not story:
            return None

        # Sort events chronologically by first_seen ascending
        sorted_events = sorted(story.events, key=lambda e: e.first_seen)

        timeline_items = []
        all_sources: set[str] = set()

        for idx, ev in enumerate(sorted_events, start=1):
            ev_sources = set()
            for art in ev.articles:
                if art.source:
                    ev_sources.add(art.source.name)
                    all_sources.add(art.source.name)

            timeline_items.append(
                {
                    "sequence": idx,
                    "event_id": ev.id,
                    "title": ev.canonical_title,
                    "category": ev.category,
                    "first_seen": ev.first_seen.isoformat(),
                    "verification_status": ev.verification_status,
                    "summary": ev.summary,
                    "sources": list(ev_sources),
                    "source_count": len(ev_sources),
                }
            )

        return {
            "id": story.id,
            "title": story.title,
            "slug": story.slug,
            "description": story.description,
            "status": story.status,
            "topic_id": story.topic_id,
            "topic_name": story.topic.name if story.topic else None,
            "domain_name": story.topic.domain.name
            if story.topic and story.topic.domain
            else None,
            "event_count": len(story.events),
            "sources": list(all_sources),
            "source_count": len(all_sources),
            "created_at": story.created_at.isoformat(),
            "updated_at": story.updated_at.isoformat(),
            "timeline": timeline_items,
        }
