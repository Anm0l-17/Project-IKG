import logging

from app.ai.providers.base import LLMResponse
from app.ai.providers.factory import get_llm_provider
from app.models.article import Article
from app.models.event import Event

logger = logging.getLogger(__name__)


class LLMReasoningEngine:
    """
    LLM Ambiguity Reasoning Engine.
    Invoked ONLY for ambiguous candidate matching cases (cross-encoder score between 0.70 and 0.82)
    or complex relationship evaluations.
    """

    def __init__(self):
        self.provider = get_llm_provider()

    async def resolve_ambiguous_match(
        self, article: Article, candidate_events: list[Event]
    ) -> LLMResponse:
        if not candidate_events or not article.headline:
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=1.0,
                explanation="No candidate events provided for reasoning.",
            )

        # Prepare evidence context for zero-shot reasoning
        candidates_context = "\n".join(
            [
                f"Candidate Event ID: {ev.id}\nTitle: {ev.canonical_title}\nCategory: {ev.category}\nSummary: {ev.summary or 'N/A'}\n---"
                for ev in candidate_events[:3]
            ]
        )

        system_instruction = """
You are an AI decision engine for India Knowledge Graph.
Your task is to determine whether a new news article describes the exact same real-world event as an existing candidate event, or if it represents a new event, follow-up, or related development.

Allowed Decisions:
- SAME_EVENT: Article describes the exact same underlying occurrence.
- FOLLOW_UP: Article describes a subsequent development of an existing event timeline.
- RELATED: Article shares entities/topics but describes a separate distinct event.
- NEW_EVENT: Article describes an entirely new, unlinked event.

Return structured JSON with keys:
"decision": "SAME_EVENT" | "FOLLOW_UP" | "RELATED" | "NEW_EVENT",
"confidence": float (0.0 to 1.0),
"explanation": "Brief rationale citing specific entities or facts",
"referenced_evidence": [list of candidate event IDs]
"""

        prompt = f"""
Incoming Article:
Headline: {article.headline}
Summary: {article.summary or "N/A"}
Text snippet: {article.clean_text[:400]}

Candidate Events to Compare:
{candidates_context}

Evaluate and return JSON decision:
"""

        try:
            response = await self.provider.generate_reasoning(
                prompt=prompt, system_instruction=system_instruction
            )
            logger.info(
                f"LLM Ambiguity Resolution: {response.decision} (Confidence: {response.confidence})"
            )
            return response
        except Exception as e:
            logger.error(f"LLM Reasoning Engine failure: {e}")
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation=f"LLM Reasoning execution error fallback: {e!s}",
            )


llm_reasoning_engine = LLMReasoningEngine()
