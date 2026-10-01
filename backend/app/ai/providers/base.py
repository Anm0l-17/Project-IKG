from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel


class LLMResponse(BaseModel):
    decision: str
    confidence: float
    explanation: str
    referenced_evidence: list[str] | None = None
    raw_response: dict[str, Any] | None = None


class LLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers.
    Follows provider abstraction pattern to isolate business logic
    from cloud (Gemini 2.5 Pro) or local (Ollama Qwen3:8B) backends.
    """

    @abstractmethod
    async def generate_reasoning(
        self,
        prompt: str,
        system_instruction: str | None = None,
        json_schema: dict[str, Any] | None = None,
    ) -> LLMResponse:
        """
        Generate structured reasoning for ambiguous event matching or classification.
        Must return structured JSON adhering to strict validation guidelines.
        """

    @abstractmethod
    async def generate_summary(
        self, context: str, summary_type: str = "citizen"
    ) -> str:
        """
        Generate factual summaries (citizen, executive, or timeline) based on verified evidence.
        """
