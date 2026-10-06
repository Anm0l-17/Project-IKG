import logging
from typing import Any

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.embeddings import embedding_service
from app.models.entity import EventEntity
from app.models.event import Event
from app.models.relationship import EventRelationship

logger = logging.getLogger(__name__)

CAUSAL_PHRASES = [
    "following the directive",
    "as a direct result",
    "triggered by",
    "in response to",
    "consequent to",
    "caused by",
    "led to",
    "prompted by",
    "owing to",
    "resulting from",
    "paved the way for",
]


class GraphEngine:
    """
    Deterministic Knowledge Graph Engine for India Knowledge Graph.
    Implements Section 13.5 of Architecture & Ontology Baseline:
    - PRECEDES: Temporal sequence within the same Story.
    - CAUSES: Causal phrasing cues + entity overlap >= 0.60 + semantic relevance >= 0.85.
    - RELATED_TO: Shared entities >= 3 and same Topic or vector similarity >= 0.75.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._cross_encoder = None
        try:
            from sentence_transformers import CrossEncoder

            self._cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except (ImportError, OSError, RuntimeError):
            self._cross_encoder = None

    def _has_causal_phrasing(self, text: str) -> bool:
        lower = text.lower()
        return any(phrase in lower for phrase in CAUSAL_PHRASES)

    def _compute_semantic_score(self, text_a: str, text_b: str) -> float:
        if self._cross_encoder:
            try:
                score = float(self._cross_encoder.predict([(text_a, text_b)])[0])
                # Sigmoid or min-max normalization if logits
                if score < 0.0 or score > 1.0:
                    import math

                    score = 1.0 / (1.0 + math.exp(-score))
                return score
            except (OverflowError, RuntimeError, TypeError, ValueError) as e:
                logger.warning(
                    f"CrossEncoder scoring failed, falling back to embeddings: {e}"
                )

        # Fallback to vector cosine similarity
        vec_a = embedding_service.generate_embedding(text_a)
        vec_b = embedding_service.generate_embedding(text_b)
        return float(embedding_service.cosine_similarity(vec_a, vec_b))

    async def infer_relationships_for_event(
        self, event_id: str
    ) -> list[EventRelationship]:
        """
        Runs deterministic edge inference rules between the specified event and candidate events.
        Persists newly discovered relationships to PostgreSQL.
        """
        stmt = (
            select(Event)
            .where(Event.id == event_id)
            .options(
                selectinload(Event.event_entities).selectinload(EventEntity.entity),
                selectinload(Event.primary_story),
                selectinload(Event.topic),
            )
        )
        res = await self.db.execute(stmt)
        event = res.scalars().first()
        if not event:
            return []

        # Find potential candidate events (in same Story, Topic, or Category)
        candidate_filters = []
        if event.primary_story_id:
            candidate_filters.append(Event.primary_story_id == event.primary_story_id)
        if event.topic_id:
            candidate_filters.append(Event.topic_id == event.topic_id)
        candidate_filters.append(Event.category == event.category)

        cand_stmt = (
            select(Event)
            .where(and_(Event.id != event_id, or_(*candidate_filters)))
            .options(
                selectinload(Event.event_entities).selectinload(EventEntity.entity)
            )
            .limit(50)
        )
        cand_res = await self.db.execute(cand_stmt)
        candidates = cand_res.scalars().all()

        # Existing relationships to avoid duplicates
        existing_stmt = select(EventRelationship).where(
            or_(
                EventRelationship.source_event_id == event_id,
                EventRelationship.target_event_id == event_id,
            )
        )
        existing_res = await self.db.execute(existing_stmt)
        existing_rels = existing_res.scalars().all()
        existing_pairs: set[tuple] = {
            (r.source_event_id, r.target_event_id, r.relationship_type)
            for r in existing_rels
        }
        existing_pairs.update(
            {
                (r.target_event_id, r.source_event_id, r.relationship_type)
                for r in existing_rels
            }
        )

        event_text = f"{event.canonical_title} {event.summary or ''}"
        event_entity_ids = {ee.entity_id for ee in event.event_entities}
        event_entity_names = {
            ee.entity.canonical_name for ee in event.event_entities if ee.entity
        }

        inferred: list[EventRelationship] = []

        for cand in candidates:
            cand_text = f"{cand.canonical_title} {cand.summary or ''}"
            cand_entity_ids = {ee.entity_id for ee in cand.event_entities}
            cand_entity_names = {
                ee.entity.canonical_name for ee in cand.event_entities if ee.entity
            }

            shared_entities = event_entity_ids & cand_entity_ids
            shared_names = event_entity_names & cand_entity_names
            total_entities = event_entity_ids | cand_entity_ids
            jaccard = len(shared_entities) / max(len(total_entities), 1)

            # Rule 1: PRECEDES (Temporal ordering within same Story)
            if (
                event.primary_story_id is not None
                and cand.primary_story_id == event.primary_story_id
            ):
                if event.first_seen < cand.first_seen:
                    pair = (event.id, cand.id, "PRECEDES")
                    if pair not in existing_pairs:
                        rel = EventRelationship(
                            source_event_id=event.id,
                            target_event_id=cand.id,
                            relationship_type="PRECEDES",
                            confidence=0.95,
                            evidence_count=1,
                            status="VALIDATED",
                            reasoning=f"Temporal sequence within Story: '{event.canonical_title}' occurred prior to '{cand.canonical_title}'.",
                        )
                        inferred.append(rel)
                        existing_pairs.add(pair)
                elif cand.first_seen < event.first_seen:
                    pair = (cand.id, event.id, "PRECEDES")
                    if pair not in existing_pairs:
                        rel = EventRelationship(
                            source_event_id=cand.id,
                            target_event_id=event.id,
                            relationship_type="PRECEDES",
                            confidence=0.95,
                            evidence_count=1,
                            status="VALIDATED",
                            reasoning=f"Temporal sequence within Story: '{cand.canonical_title}' occurred prior to '{event.canonical_title}'.",
                        )
                        inferred.append(rel)
                        existing_pairs.add(pair)

            # Rule 2: CAUSES (Causal phrasing + Entity Overlap >= 0.60 + Semantic Relevance >= 0.85 or fallback)
            has_causal = self._has_causal_phrasing(
                event_text
            ) or self._has_causal_phrasing(cand_text)
            if has_causal and jaccard >= 0.60:
                semantic_score = self._compute_semantic_score(event_text, cand_text)
                min_semantic = 0.85 if self._cross_encoder else 0.35
                if semantic_score >= min_semantic:
                    # Direction: earlier is cause, later is effect
                    if event.first_seen <= cand.first_seen:
                        source_id, target_id = event.id, cand.id
                        c_title, e_title = event.canonical_title, cand.canonical_title
                    else:
                        source_id, target_id = cand.id, event.id
                        c_title, e_title = cand.canonical_title, event.canonical_title

                    pair = (source_id, target_id, "CAUSES")
                    if pair not in existing_pairs:
                        confidence_val = (
                            round(min(semantic_score, 0.99), 2)
                            if self._cross_encoder
                            else 0.85
                        )
                        rel = EventRelationship(
                            source_event_id=source_id,
                            target_event_id=target_id,
                            relationship_type="CAUSES",
                            confidence=confidence_val,
                            evidence_count=1,
                            status="VALIDATED",
                            reasoning=f"Causal inference (overlap={jaccard:.2f}, score={semantic_score:.2f}): '{c_title}' triggered or led to '{e_title}'.",
                        )
                        inferred.append(rel)
                        existing_pairs.add(pair)

            # Rule 3: RELATED_TO (Shared Entities >= 3 + Same Topic OR Cosine Sim >= 0.75)
            if len(shared_entities) >= 3:
                is_same_topic = (
                    event.topic_id is not None and event.topic_id == cand.topic_id
                )
                sim_score = self._compute_semantic_score(event_text, cand_text)
                if is_same_topic or sim_score >= 0.75:
                    source_id = min(event.id, cand.id)
                    target_id = max(event.id, cand.id)
                    pair = (source_id, target_id, "RELATED_TO")
                    if pair not in existing_pairs:
                        names_str = ", ".join(list(shared_names)[:3])
                        rel = EventRelationship(
                            source_event_id=source_id,
                            target_event_id=target_id,
                            relationship_type="RELATED_TO",
                            confidence=round(
                                min(0.70 + 0.05 * len(shared_entities), 0.98), 2
                            ),
                            evidence_count=len(shared_entities),
                            status="VALIDATED",
                            reasoning=f"Topical affinity with {len(shared_entities)} shared entities including: {names_str}.",
                        )
                        inferred.append(rel)
                        existing_pairs.add(pair)

        if inferred:
            self.db.add_all(inferred)
            await self.db.commit()
            for r in inferred:
                await self.db.refresh(r)

        return inferred

    async def get_event_subgraph(
        self, event_id: str, depth: int = 1, min_confidence: float = 0.5
    ) -> dict[str, Any] | None:
        """
        Retrieves the ego-subgraph for an event:
        - Central Event node + connected Event nodes.
        - Connected Entity nodes (via EventEntity).
        - Directed edges between Events (EventRelationship) and Event-Entity edges.
        """
        event_stmt = (
            select(Event)
            .where(Event.id == event_id)
            .options(
                selectinload(Event.event_entities).selectinload(EventEntity.entity),
                selectinload(Event.domain),
                selectinload(Event.topic),
            )
        )
        res = await self.db.execute(event_stmt)
        central_event = res.scalars().first()
        if not central_event:
            return None

        # Fetch connected relationships
        rel_stmt = select(EventRelationship).where(
            and_(
                or_(
                    EventRelationship.source_event_id == event_id,
                    EventRelationship.target_event_id == event_id,
                ),
                EventRelationship.confidence >= min_confidence,
            )
        )
        rel_res = await self.db.execute(rel_stmt)
        relationships = rel_res.scalars().all()

        connected_event_ids = set()
        for r in relationships:
            connected_event_ids.add(r.source_event_id)
            connected_event_ids.add(r.target_event_id)
        connected_event_ids.discard(event_id)

        connected_events: list[Event] = []
        if connected_event_ids:
            conn_stmt = (
                select(Event)
                .where(Event.id.in_(list(connected_event_ids)))
                .options(
                    selectinload(Event.event_entities).selectinload(EventEntity.entity)
                )
            )
            c_res = await self.db.execute(conn_stmt)
            connected_events = c_res.scalars().all()

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        seen_node_ids = set()

        # Add central event node
        nodes.append(
            {
                "id": central_event.id,
                "label": central_event.canonical_title,
                "type": "EVENT",
                "category": central_event.category,
                "status": central_event.verification_status,
                "importance": central_event.importance_score
                or central_event.knowledge_score
                or 1.0,
                "is_central": True,
            }
        )
        seen_node_ids.add(central_event.id)

        # Add connected event nodes
        for ev in connected_events:
            if ev.id not in seen_node_ids:
                nodes.append(
                    {
                        "id": ev.id,
                        "label": ev.canonical_title,
                        "type": "EVENT",
                        "category": ev.category,
                        "status": ev.verification_status,
                        "importance": ev.importance_score or ev.knowledge_score or 1.0,
                        "is_central": False,
                    }
                )
                seen_node_ids.add(ev.id)

        # Add entities linked to central event and connected events
        all_events = [central_event] + list(connected_events)
        for ev in all_events:
            for ee in ev.event_entities:
                if ee.entity and ee.entity.id not in seen_node_ids:
                    nodes.append(
                        {
                            "id": ee.entity.id,
                            "label": ee.entity.canonical_name,
                            "type": "ENTITY",
                            "category": ee.entity.type,
                            "status": "ACTIVE",
                            "importance": ee.entity.importance or 1.0,
                            "is_central": False,
                        }
                    )
                    seen_node_ids.add(ee.entity.id)

                # Add Event -> Entity edge
                edges.append(
                    {
                        "id": f"ee_{ee.id}",
                        "source": ee.event_id,
                        "target": ee.entity_id,
                        "type": ee.relationship_type or "MENTIONS",
                        "confidence": ee.confidence or 1.0,
                        "reasoning": f"Entity extracted with {ee.confidence:.2f} confidence",
                    }
                )

        # Add Event -> Event edges
        for r in relationships:
            edges.append(
                {
                    "id": r.id,
                    "source": r.source_event_id,
                    "target": r.target_event_id,
                    "type": r.relationship_type,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning,
                }
            )

        return {
            "central_event_id": event_id,
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }

    async def get_global_graph(
        self, domain_id: str | None = None, category: str | None = None, limit: int = 40
    ) -> dict[str, Any]:
        """
        Returns a global overview slice of the Knowledge Graph for exploration.
        """
        filters = []
        if domain_id:
            filters.append(Event.domain_id == domain_id)
        if category:
            filters.append(Event.category == category)

        stmt = (
            select(Event)
            .where(and_(*filters) if filters else True)
            .options(
                selectinload(Event.event_entities).selectinload(EventEntity.entity)
            )
            .order_by(Event.knowledge_score.desc(), Event.first_seen.desc())
            .limit(limit)
        )
        res = await self.db.execute(stmt)
        events = res.scalars().all()
        event_ids = {e.id for e in events}

        if not event_ids:
            return {"nodes": [], "edges": [], "node_count": 0, "edge_count": 0}

        rel_stmt = select(EventRelationship).where(
            and_(
                EventRelationship.source_event_id.in_(list(event_ids)),
                EventRelationship.target_event_id.in_(list(event_ids)),
            )
        )
        rel_res = await self.db.execute(rel_stmt)
        relationships = rel_res.scalars().all()

        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        seen_node_ids = set()

        for ev in events:
            nodes.append(
                {
                    "id": ev.id,
                    "label": ev.canonical_title,
                    "type": "EVENT",
                    "category": ev.category,
                    "status": ev.verification_status,
                    "importance": ev.importance_score or ev.knowledge_score or 1.0,
                    "is_central": False,
                }
            )
            seen_node_ids.add(ev.id)

            for ee in ev.event_entities:
                if ee.entity and ee.entity.id not in seen_node_ids:
                    nodes.append(
                        {
                            "id": ee.entity.id,
                            "label": ee.entity.canonical_name,
                            "type": "ENTITY",
                            "category": ee.entity.type,
                            "status": "ACTIVE",
                            "importance": ee.entity.importance or 1.0,
                            "is_central": False,
                        }
                    )
                    seen_node_ids.add(ee.entity.id)

                edges.append(
                    {
                        "id": f"ee_{ee.id}",
                        "source": ee.event_id,
                        "target": ee.entity_id,
                        "type": ee.relationship_type or "MENTIONS",
                        "confidence": ee.confidence or 1.0,
                        "reasoning": "Extracted Entity Link",
                    }
                )

        for r in relationships:
            edges.append(
                {
                    "id": r.id,
                    "source": r.source_event_id,
                    "target": r.target_event_id,
                    "type": r.relationship_type,
                    "confidence": r.confidence,
                    "reasoning": r.reasoning,
                }
            )

        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
        }
