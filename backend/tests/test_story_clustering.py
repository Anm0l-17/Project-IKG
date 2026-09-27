import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Domain
from app.models.topic import Topic
from app.models.story import Story
from app.models.event import Event
from app.models.source import Source
from app.models.article import Article
from app.models.entity import Entity, EventEntity
from app.services.events.story_clustering import StoryClusteringService


@pytest.mark.asyncio
async def test_cluster_creates_new_story_for_sibling_events(db_session: AsyncSession):
    """Two UNGROUPED events in the same Topic with shared entities should spawn a new Story."""
    domain = Domain(name="Economics", slug="economics-sc")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Monetary Policy", slug="monetary-policy-sc")
    db_session.add(topic)
    await db_session.flush()

    event1 = Event(
        canonical_title="RBI holds repo rate at 6.5% in June MPC meeting",
        slug="rbi-holds-rate-june",
        category="Economics",
        domain_id=domain.id,
        topic_id=topic.id,
        grouping_status="UNGROUPED",
    )
    event2 = Event(
        canonical_title="RBI Governor signals rate cut possible if inflation eases",
        slug="rbi-governor-rate-cut-signal",
        category="Economics",
        domain_id=domain.id,
        topic_id=topic.id,
        grouping_status="UNGROUPED",
    )
    db_session.add_all([event1, event2])
    await db_session.flush()

    # Add shared entities
    ent1 = Entity(canonical_name="Reserve Bank of India", type="Organisation")
    ent2 = Entity(canonical_name="Repo Rate", type="Policy")
    db_session.add_all([ent1, ent2])
    await db_session.flush()

    for ev in [event1, event2]:
        for ent in [ent1, ent2]:
            db_session.add(EventEntity(event_id=ev.id, entity_id=ent.id))
    await db_session.commit()

    service = StoryClusteringService(db_session)
    result = await service.cluster_ungrouped_events()

    assert result["stories_created"] >= 1
    assert result["grouped_count"] >= 2

    # Verify events are now GROUPED
    await db_session.refresh(event1)
    await db_session.refresh(event2)
    assert event1.grouping_status == "GROUPED"
    assert event2.grouping_status == "GROUPED"
    assert event1.primary_story_id is not None
    assert event1.primary_story_id == event2.primary_story_id


@pytest.mark.asyncio
async def test_story_verified_with_two_independent_sources(db_session: AsyncSession):
    """Story should transition to VERIFIED when it has >= 2 events from >= 2 distinct sources."""
    domain = Domain(name="Parliament", slug="parliament-sv")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Budget Session", slug="budget-session-sv")
    db_session.add(topic)
    await db_session.flush()

    story = Story(
        topic_id=topic.id,
        title="Union Budget 2026 Narrative",
        slug="union-budget-2026-narrative",
        status="PENDING",
    )
    db_session.add(story)
    await db_session.flush()

    source1 = Source(name="GKToday", domain="gktoday.in", rss_url="https://gktoday.in/rss", trust_score=0.95)
    source2 = Source(name="The Hindu", domain="thehindu.com", rss_url="https://www.thehindu.com/rss", trust_score=0.95)
    db_session.add_all([source1, source2])
    await db_session.flush()

    event1 = Event(
        canonical_title="Budget 2026: Finance Ministry allocates Rs 1.2 lakh crore for infrastructure",
        slug="budget-2026-infra",
        category="Parliament",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        grouping_status="GROUPED",
    )
    event2 = Event(
        canonical_title="Budget 2026: New income tax slabs announced for middle class",
        slug="budget-2026-tax-slabs",
        category="Parliament",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        grouping_status="GROUPED",
    )
    db_session.add_all([event1, event2])
    await db_session.flush()

    # Each event has an article from a different source
    art1 = Article(
        source_id=source1.id,
        event_id=event1.id,
        url="https://gktoday.in/budget-infra",
        headline="Budget 2026 infra allocation",
        hash="hash_art1",
    )
    art2 = Article(
        source_id=source2.id,
        event_id=event2.id,
        url="https://thehindu.com/budget-tax",
        headline="Budget 2026 tax slabs",
        hash="hash_art2",
    )
    db_session.add_all([art1, art2])
    await db_session.commit()

    service = StoryClusteringService(db_session)
    is_verified = await service.evaluate_story_verification(story.id)

    assert is_verified is True
    await db_session.refresh(story)
    assert story.status == "VERIFIED"


@pytest.mark.asyncio
async def test_story_remains_pending_with_single_source(db_session: AsyncSession):
    """Story with events all from the same source should remain PENDING."""
    domain = Domain(name="Trade", slug="trade-sp")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="India-UK FTA Single Source", slug="india-uk-fta-sp")
    db_session.add(topic)
    await db_session.flush()

    story = Story(
        topic_id=topic.id,
        title="India UK FTA Single Source Story",
        slug="india-uk-fta-single-source",
        status="PENDING",
    )
    db_session.add(story)
    await db_session.flush()

    single_source = Source(
        name="GKToday", domain="gktoday.in", rss_url="https://gktoday.in/rss", trust_score=0.95
    )
    db_session.add(single_source)
    await db_session.flush()

    ev1 = Event(
        canonical_title="India UK FTA Round 15 commences",
        slug="india-uk-fta-round-15-sp",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        grouping_status="GROUPED",
    )
    ev2 = Event(
        canonical_title="India UK FTA negotiators meet on dairy sector",
        slug="india-uk-fta-dairy-sp",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        grouping_status="GROUPED",
    )
    db_session.add_all([ev1, ev2])
    await db_session.flush()

    # Both articles from the same single source
    art1 = Article(
        source_id=single_source.id, event_id=ev1.id,
        url="https://gktoday.in/r15", headline="FTA round 15", hash="h1sp"
    )
    art2 = Article(
        source_id=single_source.id, event_id=ev2.id,
        url="https://gktoday.in/dairy", headline="FTA dairy", hash="h2sp"
    )
    db_session.add_all([art1, art2])
    await db_session.commit()

    service = StoryClusteringService(db_session)
    is_verified = await service.evaluate_story_verification(story.id)

    assert is_verified is False
    await db_session.refresh(story)
    assert story.status == "PENDING"


@pytest.mark.asyncio
async def test_story_with_fewer_than_two_events_remains_pending(db_session: AsyncSession):
    """Story with only one event must not be promoted to VERIFIED."""
    domain = Domain(name="Defence", slug="defence-sp2")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="DRDO Projects", slug="drdo-projects-sp2")
    db_session.add(topic)
    await db_session.flush()

    story = Story(
        topic_id=topic.id,
        title="DRDO Tejas Development",
        slug="drdo-tejas-sp2",
        status="PENDING",
    )
    db_session.add(story)
    await db_session.flush()

    src = Source(name="PIB", domain="pib.gov.in", rss_url="https://pib.gov.in/rss", trust_score=0.95)
    db_session.add(src)
    await db_session.flush()

    ev = Event(
        canonical_title="DRDO successfully tests Tejas MK-2 engine",
        slug="drdo-tejas-mk2-test-sp2",
        category="Defence",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        grouping_status="GROUPED",
    )
    db_session.add(ev)
    await db_session.flush()

    art = Article(source_id=src.id, event_id=ev.id, url="https://pib.gov.in/tejas", headline="Tejas test", hash="h_tejas")
    db_session.add(art)
    await db_session.commit()

    service = StoryClusteringService(db_session)
    is_verified = await service.evaluate_story_verification(story.id)

    assert is_verified is False
    await db_session.refresh(story)
    assert story.status == "PENDING"
