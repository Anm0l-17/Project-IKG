import pytest
from app.models.base import generate_uuid7
from app.models.source import Source
from app.models.event import Event
from app.models.domain import Domain
from app.models.topic import Topic
from app.models.story import Story
from app.models.claim import Claim
from app.models.evidence import Evidence


def test_uuid7_generator():
    uuid1 = generate_uuid7()
    uuid2 = generate_uuid7()
    assert len(uuid1) == 36
    assert len(uuid2) == 36
    assert uuid1 != uuid2


def test_source_model_instantiation():
    source = Source(
        name="GKToday",
        domain="gktoday.in",
        rss_url="https://www.gktoday.in/feed/",
        is_active=True
    )
    assert source.name == "GKToday"
    assert source.domain == "gktoday.in"
    assert source.is_active is True


def test_domain_model_instantiation():
    domain = Domain(
        name="Trade",
        slug="trade",
        description="Indian Trade Policies and International Commerce"
    )
    assert domain.name == "Trade"
    assert domain.slug == "trade"


def test_topic_model_instantiation():
    topic = Topic(
        domain_id=generate_uuid7(),
        name="India-UK Trade Relations",
        slug="india-uk-trade-relations",
        status="ACTIVE"
    )
    assert topic.name == "India-UK Trade Relations"
    assert topic.status == "ACTIVE"


def test_story_model_instantiation():
    story = Story(
        topic_id=generate_uuid7(),
        title="India-UK Free Trade Agreement 2026",
        slug="india-uk-fta-2026",
        status="PENDING"
    )
    assert story.title == "India-UK Free Trade Agreement 2026"
    assert story.status == "PENDING"


def test_event_model_instantiation():
    event = Event(
        canonical_title="Union Budget 2026 Table in Parliament",
        slug="union-budget-2026-table-in-parliament",
        category="Economics",
        knowledge_score=92.5,
        verification_status="Verified",
        grouping_status="UNGROUPED"
    )
    assert event.canonical_title == "Union Budget 2026 Table in Parliament"
    assert event.category == "Economics"
    assert event.knowledge_score == 92.5
    assert event.verification_status == "Verified"
    assert event.grouping_status == "UNGROUPED"


def test_claim_model_instantiation():
    claim = Claim(
        event_id=generate_uuid7(),
        article_id=generate_uuid7(),
        claim_text="Parliament introduced the tax reform bill on Monday.",
        confidence=0.95
    )
    assert claim.claim_text == "Parliament introduced the tax reform bill on Monday."
    assert claim.confidence == 0.95


def test_evidence_model_instantiation():
    evidence = Evidence(
        article_id=generate_uuid7(),
        event_id=generate_uuid7(),
        evidence_type="EVENT_EXISTENCE",
        confidence=1.0,
        reasoning="Corroborated by independent news coverage"
    )
    assert evidence.evidence_type == "EVENT_EXISTENCE"
    assert evidence.confidence == 1.0
