import logging

from pydantic import BaseModel, ConfigDict

from app.ai.embeddings import embedding_service
from app.models.article import Article
from app.models.event import Event
from app.services.ingestion.deduplication import is_title_duplicate

logger = logging.getLogger(__name__)


class MatchResultDTO(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    is_match: bool
    event: Event | None = None
    similarity_score: float = 0.0
    stage: str = "NONE"

class CandidateMatchingService:
    """
    Implements 2-Stage Bounded Candidate Matching Cascade:
    - Stage 1 (Bi-Encoder Retrieval): Fast vector cosine similarity search (top-K = 10, threshold >= 0.70).
    - Stage 2 (Cross-Encoder Re-ranking): Pairwise deep semantic comparison (threshold >= 0.80).
    """

    def __init__(self):
        self.cross_encoder = None
        try:
            from sentence_transformers import CrossEncoder

            self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        except (ImportError, OSError, RuntimeError):
            self.cross_encoder = None

    def match_article_to_events(
        self,
        article: Article,
        pending_events: list[Event],
        stage1_threshold: float = 0.70,
        stage2_threshold: float = 0.80,
    ) -> MatchResultDTO:
        if not pending_events or not article.headline:
            return MatchResultDTO(is_match=False)

        article_text = f"{article.headline} {article.summary or ''}"
        article_vec = embedding_service.generate_embedding(article_text)

        # Stage 1: Vector Cosine Similarity Candidate Retrieval (Top K = 10)
        candidates_with_scores: list[tuple[Event, float]] = []
        for event in pending_events:
            event_text = f"{event.canonical_title} {event.summary or ''}"
            event_vec = embedding_service.generate_embedding(event_text)
            score = embedding_service.cosine_similarity(article_vec, event_vec)

            if score >= stage1_threshold:
                candidates_with_scores.append((event, score))

        # Sort candidate events by similarity score descending
        candidates_with_scores.sort(key=lambda x: x[1], reverse=True)
        top_candidates = candidates_with_scores[:10]

        if not top_candidates:
            # Fallback to token fuzzy match check
            for event in pending_events:
                if is_title_duplicate(
                    article.headline, event.canonical_title, threshold=0.75
                ):
                    return MatchResultDTO(
                        is_match=True,
                        event=event,
                        similarity_score=0.75,
                        stage="FUZZY_FALLBACK",
                    )
            return MatchResultDTO(is_match=False)

        # Stage 2: Cross-Encoder Deep Semantic Re-ranking
        if self.cross_encoder is not None:
            try:
                pairs = [
                    (article_text, f"{ev.canonical_title} {ev.summary or ''}")
                    for ev, _ in top_candidates
                ]
                cross_scores = self.cross_encoder.predict(pairs)

                best_idx = -1
                best_score = -1.0
                for idx, score in enumerate(cross_scores):
                    if score > best_score:
                        best_score = score
                        best_idx = idx

                if best_idx != -1 and best_score >= stage2_threshold:
                    matched_event = top_candidates[best_idx][0]
                    return MatchResultDTO(
                        is_match=True,
                        event=matched_event,
                        similarity_score=float(best_score),
                        stage="STAGE2_CROSS_ENCODER",
                    )
            except (RuntimeError, TypeError, ValueError) as e:
                logger.warning(f"CrossEncoder prediction failed: {e}")

        # If CrossEncoder is unavailable or below threshold, use top Stage 1 candidate if >= 0.85
        top_event, top_score = top_candidates[0]
        if top_score >= 0.85:
            return MatchResultDTO(
                is_match=True,
                event=top_event,
                similarity_score=top_score,
                stage="STAGE1_VECTOR",
            )

        return MatchResultDTO(is_match=False)


candidate_matching_service = CandidateMatchingService()
