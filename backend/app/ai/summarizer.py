import logging
from typing import Optional
from app.models.event import Event
from app.ai.providers.factory import get_llm_provider

logger = logging.getLogger(__name__)


class SummarizationService:
    """
    Multi-Style Summarization Service for generating Citizen Summaries,
    Executive Intelligence Briefs, and Timeline Summaries based on verified evidence.
    """
    def __init__(self):
        self.provider = get_llm_provider()

    async def generate_citizen_summary(self, event: Event) -> str:
        """
        Generates a clear, non-jargon citizen summary of the event.
        """
        context = f"Title: {event.canonical_title}\nCategory: {event.category}\nSummary: {event.summary or 'N/A'}"
        return await self.provider.generate_summary(context, summary_type="citizen")

    async def generate_executive_brief(self, event: Event) -> str:
        """
        Generates a bulleted executive intelligence brief for policy analysts.
        """
        context = f"Title: {event.canonical_title}\nCategory: {event.category}\nSummary: {event.summary or 'N/A'}"
        return await self.provider.generate_summary(context, summary_type="executive")

    async def generate_timeline_summary(self, event: Event) -> str:
        """
        Generates a chronological narrative summary across all attached timeline entries.
        """
        timeline_texts = []
        if hasattr(event, "timeline_entries") and event.timeline_entries:
            for entry in event.timeline_entries:
                timeline_texts.append(f"- {entry.published_at.strftime('%Y-%m-%d')}: {entry.title}")
        
        timeline_str = "\n".join(timeline_texts) if timeline_texts else "No attached timeline entries."
        context = f"Event: {event.canonical_title}\nTimeline:\n{timeline_str}"
        
        return await self.provider.generate_summary(context, summary_type="timeline")


summarization_service = SummarizationService()
