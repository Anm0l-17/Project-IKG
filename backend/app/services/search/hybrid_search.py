import logging
import re
from datetime import datetime
from typing import Any

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.embeddings import embedding_service
from app.models.event import Event
from app.models.topic import Topic

logger = logging.getLogger(__name__)


class HybridSearchService:
    """
    Hybrid Search Engine combining Lexical (Keyword/Full-Text) and Semantic (pgvector / Dense Vector)
    retrieval for Events, with Reciprocal Rank Fusion / Weighted Scoring.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    @staticmethod
    def _compute_lexical_score(
        query: str, title: str, summary: str | None
    ) -> tuple[float, str | None]:
        """
        Calculates lexical relevance score based on token overlap, title exactness, and phrase hits.
        Returns (lexical_score: float [0..1], highlight_snippet: Optional[str]).
        """
        cleaned_query = query.lower().strip()
        query_tokens = set(re.findall(r"\w+", cleaned_query))
        if not query_tokens:
            return 0.0, None

        title_lower = title.lower()
        summary_lower = (summary or "").lower()

        # 1. Exact phrase in title (massive boost)
        if cleaned_query in title_lower:
            phrase_score = 0.5
        elif any(token in title_lower for token in query_tokens):
            phrase_score = 0.25
        else:
            phrase_score = 0.0

        # 2. Token overlap ratio across title + summary
        target_tokens = set(re.findall(r"\w+", f"{title_lower} {summary_lower}"))
        overlap = query_tokens.intersection(target_tokens)
        token_coverage = len(overlap) / len(query_tokens)

        # 3. Frequency boost
        combined_text = f"{title_lower} {summary_lower}"
        freq_count = sum(combined_text.count(t) for t in query_tokens)
        freq_factor = min(0.2, freq_count * 0.04)

        raw_score = (phrase_score * 0.4) + (token_coverage * 0.4) + freq_factor
        lexical_score = min(1.0, max(0.0, raw_score))

        # Extract highlight snippet from summary
        snippet = None
        if summary:
            # find first matching token
            first_match_idx = -1
            for token in query_tokens:
                pos = summary_lower.find(token)
                if pos != -1 and (first_match_idx == -1 or pos < first_match_idx):
                    first_match_idx = pos

            if first_match_idx != -1:
                start = max(0, first_match_idx - 60)
                end = min(len(summary), first_match_idx + 140)
                snip = summary[start:end].strip()
                if start > 0:
                    snip = "..." + snip
                if end < len(summary):
                    snip = snip + "..."
                snippet = snip
            else:
                snippet = summary[:160] + ("..." if len(summary) > 160 else "")

        return lexical_score, snippet

    async def search(
        self,
        query: str,
        mode: str = "hybrid",
        category: str | None = None,
        verification_status: str | None = None,
        topic_id: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> dict[str, Any]:
        """
        Executes hybrid, semantic, or lexical search across Events.
        """
        mode = mode.lower().strip()
        if mode not in ("hybrid", "semantic", "lexical"):
            mode = "hybrid"

        query_cleaned = query.strip()
        if not query_cleaned:
            return {
                "query": query,
                "mode": mode,
                "total_results": 0,
                "results": [],
            }

        # Build candidate query filters
        stmt = select(Event).options(
            selectinload(Event.topic).selectinload(Topic.domain),
        )

        conditions = []
        if category:
            conditions.append(Event.category == category)
        if verification_status:
            conditions.append(Event.verification_status == verification_status)
        if topic_id:
            conditions.append(Event.topic_id == topic_id)
        if from_date:
            conditions.append(Event.first_seen >= from_date)
        if to_date:
            conditions.append(Event.first_seen <= to_date)

        # Lexical pre-filter if lexical-only mode
        if mode == "lexical":
            terms = re.findall(r"\w+", query_cleaned)
            term_clauses = [
                or_(
                    Event.canonical_title.ilike(f"%{t}%"),
                    Event.summary.ilike(f"%{t}%"),
                )
                for t in terms[:5]
            ]
            if term_clauses:
                conditions.append(or_(*term_clauses))

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # Retrieve candidates (fetch up to 100 candidates to score & rank)
        candidate_limit = max(100, limit * 3)
        stmt = stmt.order_by(desc(Event.last_updated)).limit(candidate_limit)

        res = await self.session.execute(stmt)
        candidates = list(res.scalars().all())

        if not candidates:
            return {
                "query": query,
                "mode": mode,
                "total_results": 0,
                "results": [],
            }

        # Compute Query Vector for semantic / hybrid modes
        query_vector = None
        if mode in ("semantic", "hybrid"):
            query_vector = embedding_service.generate_embedding(query_cleaned)

        scored_results: list[dict[str, Any]] = []

        for ev in candidates:
            # 1. Lexical Scoring
            lexical_score, snippet = self._compute_lexical_score(
                query_cleaned, ev.canonical_title, ev.summary
            )

            # 2. Semantic Scoring
            semantic_score = 0.0
            if mode in ("semantic", "hybrid") and query_vector:
                # Use stored embedding or calculate fallback
                ev_vec = ev.embedding
                if not ev_vec:
                    text = f"{ev.canonical_title}. {ev.summary or ''}"
                    ev_vec = embedding_service.generate_embedding(text)
                sim = embedding_service.cosine_similarity(query_vector, ev_vec)
                if embedding_service.model is None:
                    # In sparse fallback embedding, scale dot-product similarity
                    semantic_score = min(1.0, max(0.0, sim * 2.5))
                else:
                    # SentenceTransformer / cosine similarity [-1.0, 1.0] -> [0.0, 1.0]
                    semantic_score = max(0.0, min(1.0, (sim + 1.0) / 2.0))

            # 3. Combined Final Relevance Score
            if mode == "lexical":
                final_score = lexical_score
                match_type = "LEXICAL"
            elif mode == "semantic":
                final_score = semantic_score
                match_type = "SEMANTIC"
            else:  # hybrid
                # 45% lexical + 55% semantic
                final_score = (0.45 * lexical_score) + (0.55 * semantic_score)

                # Small quality boost for VERIFIED events (+0.05) and high knowledge score
                if ev.verification_status == "VERIFIED":
                    final_score += 0.05
                final_score += min(0.05, ev.knowledge_score * 0.05)
                final_score = min(1.0, max(0.0, final_score))

                # Determine match tag
                if lexical_score >= 0.35 and semantic_score >= 0.55:
                    match_type = "HYBRID"
                elif semantic_score >= 0.60:
                    match_type = "SEMANTIC"
                elif lexical_score >= 0.35:
                    match_type = "LEXICAL"
                else:
                    match_type = "RELEVANCE"

            # Filter out near-zero noise
            threshold = 0.15 if mode in ("lexical", "semantic") else 0.25
            if final_score < threshold:
                continue

            scored_results.append(
                {
                    "id": ev.id,
                    "title": ev.canonical_title,
                    "slug": ev.slug,
                    "category": ev.category,
                    "subcategory": ev.subcategory,
                    "summary": ev.summary,
                    "highlight_snippet": snippet
                    or (ev.summary[:150] if ev.summary else None),
                    "knowledge_score": ev.knowledge_score,
                    "verification_status": ev.verification_status,
                    "grouping_status": ev.grouping_status,
                    "primary_story_id": ev.primary_story_id,
                    "topic_name": ev.topic.name if ev.topic else None,
                    "domain_name": ev.topic.domain.name
                    if ev.topic and ev.topic.domain
                    else None,
                    "first_seen": ev.first_seen.isoformat(),
                    "last_updated": ev.last_updated.isoformat(),
                    "relevance_score": round(final_score, 4),
                    "lexical_score": round(lexical_score, 4),
                    "semantic_score": round(semantic_score, 4),
                    "match_type": match_type,
                }
            )

        # Sort by relevance_score descending
        scored_results.sort(key=lambda r: r["relevance_score"], reverse=True)

        total_matches = len(scored_results)
        paged_results = scored_results[offset : offset + limit]

        return {
            "query": query,
            "mode": mode,
            "total_results": total_matches,
            "results": paged_results,
        }

    async def backfill_event_embeddings(self, batch_size: int = 100) -> int:
        """
        Backfills vector embeddings for events that have null embeddings.
        """
        stmt = select(Event).where(Event.embedding.is_(None)).limit(batch_size)
        res = await self.session.execute(stmt)
        events = res.scalars().all()

        target_events = [ev for ev in events if not ev.embedding]
        if not target_events:
            # Fallback if dialect stored JSON 'null' string
            all_stmt = select(Event).limit(batch_size)
            all_res = await self.session.execute(all_stmt)
            target_events = [ev for ev in all_res.scalars().all() if not ev.embedding]

        updated_count = 0
        for ev in target_events:
            text = f"{ev.canonical_title}. {ev.summary or ''}"
            vec = embedding_service.generate_embedding(text)
            ev.embedding = vec
            updated_count += 1

        if updated_count > 0:
            await self.session.commit()

        return updated_count
