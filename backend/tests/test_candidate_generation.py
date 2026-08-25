import pytest
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.article import Article
from app.models.source import Source
from app.models.event import Event
from app.models.entity import Entity
from app.models.evidence import Evidence
from app.models.enums import VerificationStatus, GroupingStatus, DomainCategory, EvidenceType, EventLifecycleState
from app.services.events.candidate_generation import CandidateEventService


@pytest.mark.asyncio
async def test_article_with_ministry_generates_event_and_evidence(db_session: AsyncSession):
    # Setup source
    source = Source(name="Test Source", domain="test.com")
    db_session.add(source)
    await db_session.commit()

    # Setup article
    article = Article(
        source_id=source.id,
        url="http://test.com/1",
        headline="Ministry of Education announces new policy",
        summary="The Ministry of Education has announced a new educational policy.",
        published_at=datetime.now(timezone.utc),
        scraped_at=datetime.now(timezone.utc),
        clean_text="Clean text",
        hash="hash1"
    )
    db_session.add(article)
    await db_session.commit()

    service = CandidateEventService(db_session)
    events = await service.generate_candidates_from_articles([article])

    assert len(events) == 1
    event = events[0]
    assert event.status == EventLifecycleState.PENDING.value
    assert event.verification_status == VerificationStatus.PENDING.value
    assert event.grouping_status == GroupingStatus.UNGROUPED.value
    assert event.category == DomainCategory.PARLIAMENT.value
    assert event.canonical_article_id == article.id
    
    # Check Evidence link creation
    await db_session.refresh(event, ['evidence_items'])
    assert len(event.evidence_items) == 1
    evidence = event.evidence_items[0]
    assert evidence.article_id == article.id
    assert evidence.evidence_type == EvidenceType.EVENT_EXISTENCE.value
    assert evidence.confidence == 1.0

    # Check entities
    await db_session.refresh(event, ['event_entities'])
    assert len(event.event_entities) > 0
    entity_id = event.event_entities[0].entity_id
    entity = await db_session.get(Entity, entity_id)
    assert entity.canonical_name == "Ministry of Education"
    assert entity.type == "Ministry"


@pytest.mark.asyncio
async def test_article_without_entities_still_generates_event(db_session: AsyncSession):
    source = Source(name="Test Source 2", domain="test2.com")
    db_session.add(source)
    await db_session.commit()

    article = Article(
        source_id=source.id,
        url="http://test2.com/1",
        headline="Weather forecast for Delhi",
        summary="Sunny today.",
        published_at=datetime.now(timezone.utc),
        scraped_at=datetime.now(timezone.utc),
        clean_text="Clean text",
        hash="hash2"
    )
    db_session.add(article)
    await db_session.commit()

    service = CandidateEventService(db_session)
    events = await service.generate_candidates_from_articles([article])

    assert len(events) == 1
    event = events[0]
    assert event.status == EventLifecycleState.PENDING.value
    assert event.category == DomainCategory.CURRENT_AFFAIRS.value
    
    # State 'Delhi' should be extracted
    await db_session.refresh(event, ['event_entities'])
    entity = await db_session.get(Entity, event.event_entities[0].entity_id)
    assert entity.canonical_name == "Delhi"
    assert entity.type == "State"


@pytest.mark.asyncio
async def test_duplicate_articles_dont_spawn_duplicate_events(db_session: AsyncSession):
    source = Source(name="Test Source 3", domain="test3.com")
    db_session.add(source)
    await db_session.commit()

    article = Article(
        source_id=source.id,
        url="http://test3.com/1",
        headline="Test Event",
        summary="Summary",
        published_at=datetime.now(timezone.utc),
        scraped_at=datetime.now(timezone.utc),
        clean_text="Clean text",
        hash="hash3"
    )
    db_session.add(article)
    await db_session.commit()

    service = CandidateEventService(db_session)
    events = await service.generate_candidates_from_articles([article])
    assert len(events) == 1

    # Second pass with same article object (now it has event_id)
    events2 = await service.generate_candidates_from_articles([article])
    assert len(events2) == 0

