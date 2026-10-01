import logging

from app.ai.providers.base import LLMProvider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.ollama import OllamaLLMProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_llm_provider() -> LLMProvider:
    """
    Factory function returning the configured LLMProvider instance based on settings.LLM_PROVIDER.
    Defaults to Gemini Pro in production, falling back to Ollama Qwen3:8B.
    """
    provider_type = settings.LLM_PROVIDER.lower()
    if provider_type == "gemini":
        return GeminiLLMProvider()
    elif provider_type == "ollama":
        return OllamaLLMProvider()
    else:
        logger.warning(
            f"Unknown LLM_PROVIDER '{provider_type}'. Defaulting to GeminiLLMProvider."
        )
        return GeminiLLMProvider()
