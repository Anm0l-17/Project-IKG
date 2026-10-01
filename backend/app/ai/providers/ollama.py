import json
import logging
from typing import Any

import httpx

from app.ai.providers.base import LLMProvider, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaLLMProvider(LLMProvider):
    """
    Concrete implementation for local Ollama Qwen3:8B LLM provider.
    Enables offline local development, testing, and cost-free fallback.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL

    async def generate_reasoning(
        self,
        prompt: str,
        system_instruction: str | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": f"{system_instruction or ''}\n\n{prompt}\n\nReturn JSON only.",
            "format": "json",
            "stream": False,
            "options": {"temperature": 0.0},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    return LLMResponse(
                        decision="NEW_EVENT",
                        confidence=0.5,
                        explanation=f"Ollama returned HTTP status {res.status_code}.",
                    )

                data = res.json()
                raw_response = data.get("response", "{}")
                parsed = json.loads(raw_response)

                return LLMResponse(
                    decision=parsed.get("decision", "NEW_EVENT"),
                    confidence=float(parsed.get("confidence", 0.75)),
                    explanation=parsed.get(
                        "explanation", "Reasoning generated via Ollama Qwen3:8B."
                    ),
                    referenced_evidence=parsed.get("referenced_evidence", []),
                    raw_response=parsed,
                )
        except Exception as e:
            logger.warning(f"Ollama generate_reasoning execution error: {e}")
            return LLMResponse(
                decision="NEW_EVENT",
                confidence=0.5,
                explanation=f"Ollama offline fallback: {e!s}",
            )

    async def generate_summary(
        self, context: str, summary_type: str = "citizen"
    ) -> str:
        url = f"{self.base_url}/api/generate"
        prompt = f"Summarize the following verified Indian news event into a clear {summary_type} summary:\n\n{context}"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip() or context[:300]
        except Exception as e:
            logger.warning(f"Ollama generate_summary execution error: {e}")

        return f"Summary ({summary_type}): {context[:250]}..."
