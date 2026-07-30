from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LLMResponse(BaseModel):
    decision: str
    confidence: float
    explanation: str
    referenced_evidence: Optional[list[str]] = None
    raw_response: Optional[Dict[str, Any]] = None


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
        system_instruction: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None
    ) -> LLMResponse:
        """
        Generate structured reasoning for ambiguous event matching or classification.
        Must return structured JSON adhering to strict validation guidelines.
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        context: str,
        summary_type: str = "citizen"
    ) -> str:
        """
        Generate factual summaries (citizen, executive, or timeline) based on verified evidence.
        """
        pass
