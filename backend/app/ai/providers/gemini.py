import json
import logging
from typing import Any

import httpx
from google.genai import errors

from app.ai.providers.base import LLMProvider, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

KNOWN_PLACEHOLDER_KEYS: frozenset[str] = frozenset({
    "your_gemini_api_key_here",
    "your_api_key_here",
    "placeholder",
    "changeme",
    "none",
    "null",
})


class GeminiLLMProvider(LLMProvider):
    """
    Concrete implementation for Google Gemini Pro cloud LLM provider.
    Uses google-genai SDK with structured JSON mode.
    """

    def __init__(self, api_key: str | None = None):
        # Explicit None semantics: empty string does not fall back to settings.
        self.api_key = settings.GEMINI_API_KEY if api_key is None else api_key
        self.client = None

        key_status = self._classify_key(self.api_key)
        if key_status != "configured":
            # Never log credential values; log only the classification.
            logger.warning(
                "Gemini API key is %s. Provider running in deterministic fallback mode.",
                key_status,
            )
            return

        try:
            from google import genai

            self.client = genai.Client(api_key=self.api_key)
        except (ImportError, RuntimeError, ValueError) as e:
            logger.warning("Failed to initialize Gemini Client: %s", e)

    @property
    def is_available(self) -> bool:
        """Returns True if the provider client is initialized and ready."""
        return self.client is not None

    @staticmethod
    def _classify_key(key: str | None) -> str:
        """Classify API key status without exposing secrets in logs."""
        if not key or not key.strip():
            return "empty"
        if key.strip().lower() in KNOWN_PLACEHOLDER_KEYS:
            return "placeholder"
        return "configured"

    def _log_unavailable_alert(self) -> None:
        """Emit operational health warnings, escalating to ERROR in production."""
        if settings.APP_ENV == "production":
            logger.error(
                "OPERATIONAL ALERT: Gemini provider unavailable in production environment. "
                "Returning fallback response."
            )
        else:
            logger.warning(
                "Gemini API key missing, unconfigured, or client uninitialized. "
                "Returning fallback LLM response."
            )

    async def generate_reasoning(
        self,
        prompt: str,
        system_instruction: str | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        if self.client is None:
            self._log_unavailable_alert()
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation="Gemini client uninitialized (fallback mode).",
            )

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                system_instruction=system_instruction
                or "You are an AI decision engine for event matching. Return structured JSON matching the requested schema.",
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-pro", contents=prompt, config=config
            )
            raw_text = response.text or "{}"
            parsed = json.loads(raw_text)

            return LLMResponse(
                decision=parsed.get("decision", "NEW_EVENT"),
                confidence=float(parsed.get("confidence", 0.8)),
                explanation=parsed.get(
                    "explanation", "Reasoning generated via Gemini Pro."
                ),
                referenced_evidence=parsed.get("referenced_evidence", []),
                raw_response=parsed,
            )
        except (
            errors.APIError,
            httpx.HTTPError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
        ) as e:
            # Specific handling: SDK errors, network transport failures, JSON decode errors, response shape errors
            logger.exception("Gemini generate_reasoning provider error")
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation=f"Gemini API execution error: {e!s}",
            )
        except Exception as e:
            # Final boundary safety net to prevent unhandled provider exceptions from crashing ingestion pipelines
            logger.exception(
                "Unexpected Gemini generate_reasoning boundary failure"
            )
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation=f"Gemini API execution error: {e!s}",
            )

    async def generate_summary(
        self, context: str, summary_type: str = "citizen"
    ) -> str:
        if self.client is None:
            self._log_unavailable_alert()
            return f"Summary ({summary_type}): {context[:250]}..."

        try:
            from google.genai import types

            prompt = f"Generate a clear, evidence-backed {summary_type} summary based on the following verified event text:\n\n{context}"
            config = types.GenerateContentConfig(
                temperature=0.2,
                system_instruction="You are a senior news editor summarizing verified events for Indian affairs. Be objective, concise, and factual.",
            )
            response = self.client.models.generate_content(
                model="gemini-2.5-pro", contents=prompt, config=config
            )
            text = (response.text or "").strip()
            return (
                text if text else f"Summary ({summary_type}): {context[:250]}..."
            )
        except (
            errors.APIError,
            httpx.HTTPError,
            AttributeError,
            RuntimeError,
            TypeError,
            ValueError,
        ):
            # Specific handling: SDK errors, network transport failures, response shape errors
            logger.exception("Gemini generate_summary provider error")
            return f"Summary ({summary_type}): {context[:250]}..."
        except Exception:
            # Final boundary safety net to prevent unhandled provider exceptions from crashing summary generation
            logger.exception(
                "Unexpected Gemini generate_summary boundary failure"
            )
            return f"Summary ({summary_type}): {context[:250]}..."
