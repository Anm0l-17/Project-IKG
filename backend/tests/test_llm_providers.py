import pytest

from app.ai.providers.base import LLMProvider, LLMResponse
from app.ai.providers.factory import get_llm_provider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.ollama import OllamaLLMProvider
from app.ai.reasoning import llm_reasoning_engine
from app.ai.summarizer import summarization_service
from app.models.article import Article
from app.models.event import Event


def test_provider_factory():
    provider = get_llm_provider()
    assert isinstance(provider, LLMProvider)


@pytest.mark.asyncio
async def test_ollama_fallback_reasoning():
    provider = OllamaLLMProvider(base_url="http://invalid-localhost:11434")
    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5


@pytest.mark.asyncio
async def test_gemini_fallback_reasoning():
    provider = GeminiLLMProvider(api_key="")
    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5


@pytest.mark.asyncio
async def test_llm_reasoning_engine_fallback():
    article = Article(
        headline="Cabinet approves new Semiconductor Mission", clean_text="Test snippet"
    )
    event = Event(
        canonical_title="Cabinet approves Semiconductor Scheme", category="Economics"
    )

    res = await llm_reasoning_engine.resolve_ambiguous_match(article, [event])
    assert isinstance(res, LLMResponse)
    assert res.decision in ("SAME_EVENT", "FOLLOW_UP", "RELATED", "NEW_EVENT")


@pytest.mark.asyncio
async def test_summarization_service_fallback():
    event = Event(
        canonical_title="Union Budget 2026 Table in Parliament",
        category="Economics",
        summary="Budget overview text.",
    )
    summary = await summarization_service.generate_citizen_summary(event)
    assert isinstance(summary, str)
    assert len(summary) > 0
