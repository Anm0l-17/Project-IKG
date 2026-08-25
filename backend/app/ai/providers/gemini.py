import json
import logging
from typing import Dict, Any, Optional
from app.ai.providers.base import LLMProvider, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class GeminiLLMProvider(LLMProvider):
    """
    Concrete implementation for Google Gemini Pro cloud LLM provider.
    Uses google-genai SDK with structured JSON mode.
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini Client: {e}")

    async def generate_reasoning(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        if self.client is None:
            logger.warning("Gemini API key missing or client uninitialized. Returning fallback LLM response.")
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation="Gemini client uninitialized (fallback mode)."
            )

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                system_instruction=system_instruction or "You are an AI decision engine for event matching. Return structured JSON matching the requested schema."
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=config
            )
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)

            return LLMResponse(
                decision=parsed.get("decision", "NEW_EVENT"),
                confidence=float(parsed.get("confidence", 0.8)),
                explanation=parsed.get("explanation", "Reasoning generated via Gemini Pro."),
                referenced_evidence=parsed.get("referenced_evidence", []),
                raw_response=parsed
            )
        except Exception as e:
            logger.error(f"Gemini generate_reasoning failed: {e}")
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation=f"Gemini API execution error: {str(e)}"
            )

    async def generate_summary(
        self,
        context: str,
        summary_type: str = "citizen"
    ) -> str:
        if self.client is None:
            return f"Summary ({summary_type}): {context[:250]}..."

        try:
            from google.genai import types
            prompt = f"Generate a clear, evidence-backed {summary_type} summary based on the following verified event text:\n\n{context}"
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction="You are a senior news editor summarizing verified events for Indian affairs. Be objective, concise, and factual."
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=config
            )
            return response.text or context[:300]
        except Exception as e:
            logger.error(f"Gemini generate_summary failed: {e}")
            return f"Summary ({summary_type}): {context[:250]}..."
