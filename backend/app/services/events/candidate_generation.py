import logging
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.entity import Entity, EventEntity
from app.models.enums import (
    DomainCategory,
    EventLifecycleState,
    EvidenceType,
    GroupingStatus,
    VerificationStatus,
)
from app.models.event import Event
from app.models.evidence import Evidence

logger = logging.getLogger(__name__)

from app.services.events.verification import VerificationEngine


class CandidateEventService:
    """
    Handles the creation of candidate events from newly ingested articles.
    Implements simple heuristic entity extraction for the MVP before full SpaCy integration.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_candidates_from_articles(
        self, articles: list[Article]
    ) -> list[Event]:
        new_events = []
        verification_engine = VerificationEngine(self.db)

        for article in articles:
            # Skip if article already belongs to an event
            if article.event_id:
                continue

            # First, evaluate if this article corroborates an existing PENDING event
            corroborated = await verification_engine.evaluate_incoming_article_against_pending_events(
                article
            )
            if corroborated:
                logger.info(
                    f"Article {article.id} corroborated an existing PENDING event."
                )
                continue

            # If uncorroborated, generate a new Candidate Event
            event = await self._create_event_from_article(article)

            # Create explicit Evidence link
            evidence = Evidence(
                article_id=article.id,
                event_id=event.id,
                evidence_type=EvidenceType.EVENT_EXISTENCE.value,
                confidence=1.0,
                reasoning="Candidate event created from initial single-source article ingestion.",
            )
            self.db.add(evidence)

            # Extract Entities
            await self._extract_and_link_entities(article, event)

            new_events.append(event)
            logger.info(
                f"Generated candidate event {event.id} from article {article.id}"
            )

        if new_events:
            await self.db.commit()
            for ev in new_events:
                await self.db.refresh(ev)

        return new_events

    def _classify_domain(self, text: str) -> str:
        text_lower = text.lower()

        def has_any_term(terms: list[str]) -> bool:
            for term in terms:
                pattern = rf"\b{re.escape(term)}\b"
                if re.search(pattern, text_lower):
                    return True
            return False

        if has_any_term(
            ["parliament", "lok sabha", "rajya sabha", "bill", "act", "mou"]
        ):
            return DomainCategory.PARLIAMENT.value
        if has_any_term(
            ["gdp", "economy", "rbi", "inflation", "tax", "budget", "finance"]
        ):
            return DomainCategory.ECONOMICS.value
        if has_any_term(
            ["trade", "export", "import", "fta", "tariff", "commerce"]
        ):
            return DomainCategory.TRADE.value
        if has_any_term(
            [
                "army",
                "navy",
                "air force",
                "defence",
                "defense",
                "military",
                "weapon",
            ]
        ):
            return DomainCategory.DEFENCE.value
        if has_any_term(
            [
                "bilateral",
                "summit",
                "diplomacy",
                "ambassador",
                "foreign",
                "un",
                "geopolitics",
            ]
        ):
            return DomainCategory.GEOPOLITICS.value
        return DomainCategory.CURRENT_AFFAIRS.value

    async def _create_event_from_article(self, article: Article) -> Event:
        # Title limit 80 chars for Event name
        headline = article.headline or ""
        name = headline[:80] + ("..." if len(headline) > 80 else "")
        slug = re.sub(r"[^a-z0-9]+", "-", headline.lower()).strip("-")

        # Append hash to ensure slug uniqueness
        article_hash = getattr(article, "hash", "unknown")
        slug = f"{slug[:100]}-{article_hash[:8]}"

        text_content = f"{headline} {article.summary or ''}"
        domain_category = self._classify_domain(text_content)

        event = Event(
            canonical_title=name,
            slug=slug,
            category=domain_category,
            summary=article.summary,
            primary_story_id=None,
            canonical_article_id=article.id,
            grouping_status=GroupingStatus.UNGROUPED.value,
            verification_status=VerificationStatus.PENDING.value,
            status=EventLifecycleState.PENDING.value,
        )
        self.db.add(event)
        await self.db.flush()  # Flush to get event id

        # Initialize Verification state
        v_engine = VerificationEngine(self.db)
        await v_engine.initialize_verification_for_event(event, article)

        # Link Article to Event as transitional shortcut
        article.event_id = event.id
        self.db.add(article)

        return event

    async def _extract_and_link_entities(
        self, article: Article, event: Event
    ) -> list[Entity]:
        from app.ai.ner import entity_extraction_service

        text = f"{article.headline} {article.summary or ''}"

        extracted_dtos = entity_extraction_service.extract_entities(text)
        created_entities = []

        for dto in extracted_dtos:
            stmt = select(Entity).where(Entity.canonical_name == dto.canonical_name)
            res = await self.db.execute(stmt)
            entity = res.scalar_one_or_none()

            if not entity:
                entity = Entity(
                    canonical_name=dto.canonical_name,
                    type=dto.entity_type,
                )
                self.db.add(entity)
                await self.db.flush()

            link = EventEntity(
                event_id=event.id,
                entity_id=entity.id,
                relationship_type="MENTIONS",
                confidence=dto.confidence,
            )
            self.db.add(link)
            created_entities.append(entity)

        return created_entities
