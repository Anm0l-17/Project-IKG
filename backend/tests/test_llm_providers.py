import logging
from unittest.mock import MagicMock

import httpx
import pytest
from google.genai import errors

from app.ai.providers.base import LLMProvider, LLMResponse
from app.ai.providers.factory import get_llm_provider
from app.ai.providers.gemini import GeminiLLMProvider
from app.ai.providers.ollama import OllamaLLMProvider
from app.ai.reasoning import LLMReasoningEngine, llm_reasoning_engine
from app.ai.summarizer import SummarizationService, summarization_service
from app.core.config import settings
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


def test_gemini_api_key_none_uses_settings(monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test_settings_key")
    provider = GeminiLLMProvider(api_key=None)
    assert provider.api_key == "test_settings_key"


@pytest.mark.asyncio
async def test_gemini_empty_api_key_disables_gemini():
    provider = GeminiLLMProvider(api_key="")
    assert provider.api_key == ""
    assert provider.client is None
    assert not provider.is_available
    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "placeholder",
    [
        "your_gemini_api_key_here",
        "YOUR_GEMINI_API_KEY_HERE",
        "your_api_key_here",
        "placeholder",
        "changeme",
        "none",
        "null",
        "   ",
    ],
)
async def test_gemini_placeholder_keys_disable_gemini(placeholder):
    provider = GeminiLLMProvider(api_key=placeholder)
    assert provider.client is None
    assert not provider.is_available
    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5


def test_gemini_logging_does_not_expose_secrets(caplog):
    placeholder = "your_gemini_api_key_here"
    with caplog.at_level(logging.WARNING):
        provider = GeminiLLMProvider(api_key=placeholder)
    assert provider.client is None
    # Secret must never appear in log records
    assert placeholder not in caplog.text
    # Classification must be present
    assert "Gemini API key is placeholder" in caplog.text


def test_gemini_logging_empty_key_classification(caplog):
    with caplog.at_level(logging.WARNING):
        provider = GeminiLLMProvider(api_key="")
    assert provider.client is None
    assert "Gemini API key is empty" in caplog.text


@pytest.mark.asyncio
async def test_gemini_production_operational_alert(monkeypatch, caplog):
    monkeypatch.setattr(settings, "APP_ENV", "production")
    provider = GeminiLLMProvider(api_key="")
    with caplog.at_level(logging.ERROR):
        res = await provider.generate_reasoning("Test prompt")
    assert res.decision == "NEW_EVENT"
    assert (
        "OPERATIONAL ALERT: Gemini provider unavailable in production"
        in caplog.text
    )


@pytest.mark.asyncio
async def test_gemini_sdk_api_failure_fallback():
    provider = GeminiLLMProvider(api_key="mock-configured-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = errors.ClientError(
        400,
        {
            "error": {
                "code": 400,
                "message": "API key not valid.",
                "status": "INVALID_ARGUMENT",
            }
        },
        None,
    )
    provider.client = mock_client

    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5
    assert "Gemini API execution error" in res.explanation

    summary = await provider.generate_summary("Event text", summary_type="citizen")
    assert summary.startswith("Summary (citizen):")
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_gemini_network_failure_fallback():
    provider = GeminiLLMProvider(api_key="mock-configured-key")
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = httpx.ConnectError(
        "Connection refused",
        request=MagicMock(),
    )
    provider.client = mock_client

    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5
    assert "Gemini API execution error" in res.explanation

    summary = await provider.generate_summary("Event text", summary_type="executive")
    assert summary.startswith("Summary (executive):")
    assert len(summary) > 0


@pytest.mark.asyncio
async def test_gemini_malformed_json_fallback():
    provider = GeminiLLMProvider(api_key="mock-configured-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "{invalid_json: true, unterminated"
    mock_client.models.generate_content.return_value = mock_response
    provider.client = mock_client

    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5
    assert "Gemini API execution error" in res.explanation


@pytest.mark.asyncio
async def test_gemini_summary_fallback_remains_non_empty():
    provider = GeminiLLMProvider(api_key="")
    # Empty context
    summary_empty = await provider.generate_summary("", summary_type="citizen")
    assert isinstance(summary_empty, str)
    assert len(summary_empty) > 0
    assert summary_empty == "Summary (citizen): ..."

    # Context with text
    summary_with_text = await provider.generate_summary(
        "Event text", summary_type="timeline"
    )
    assert isinstance(summary_with_text, str)
    assert len(summary_with_text) > 0
    assert "Event text" in summary_with_text

    # Mock client returning empty string
    mock_provider = GeminiLLMProvider(api_key="mock-configured-key")
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "   "
    mock_client.models.generate_content.return_value = mock_response
    mock_provider.client = mock_client

    summary_blank = await mock_provider.generate_summary(
        "Event fallback", summary_type="citizen"
    )
    assert len(summary_blank) > 0
    assert "Event fallback" in summary_blank


@pytest.mark.asyncio
async def test_gemini_fallback_reasoning():
    provider = GeminiLLMProvider(api_key="")
    res = await provider.generate_reasoning("Test prompt")
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5


@pytest.mark.asyncio
async def test_reasoning_and_summarization_services_use_provider_fallback(
    monkeypatch,
):
    unconfigured_provider = GeminiLLMProvider(api_key="")
    engine = LLMReasoningEngine()
    engine.provider = unconfigured_provider
    summarizer = SummarizationService()
    summarizer.provider = unconfigured_provider

    article = Article(
        headline="Cabinet approves new Semiconductor Mission",
        clean_text="Test snippet",
    )
    event = Event(
        canonical_title="Cabinet approves Semiconductor Scheme",
        category="Economics",
    )

    res = await engine.resolve_ambiguous_match(article, [event])
    assert isinstance(res, LLMResponse)
    assert res.decision == "NEW_EVENT"
    assert res.confidence == 0.5

    summary = await summarizer.generate_citizen_summary(event)
    assert isinstance(summary, str)
    assert len(summary) > 0
    assert summary.startswith("Summary (citizen):")


@pytest.mark.asyncio
async def test_llm_reasoning_engine_fallback():
    article = Article(
        headline="Cabinet approves new Semiconductor Mission",
        clean_text="Test snippet",
    )
    event = Event(
        canonical_title="Cabinet approves Semiconductor Scheme",
        category="Economics",
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
