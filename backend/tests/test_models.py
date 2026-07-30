import pytest
from app.models.base import generate_uuid7
from app.models.source import Source
from app.models.event import Event


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
        rss_url="https://www.gktoday.in/feed/"
    )
    assert source.name == "GKToday"
    assert source.domain == "gktoday.in"
    assert source.is_active is True


def test_event_model_instantiation():
    event = Event(
        canonical_title="Union Budget 2026 Table in Parliament",
        slug="union-budget-2026-table-in-parliament",
        category="Economics",
        knowledge_score=92.5,
        verification_status="Verified"
    )
    assert event.canonical_title == "Union Budget 2026 Table in Parliament"
    assert event.category == "Economics"
    assert event.knowledge_score == 92.5
    assert event.verification_status == "Verified"
