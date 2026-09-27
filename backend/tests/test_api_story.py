import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Domain
from app.models.topic import Topic
from app.models.story import Story
from app.models.event import Event
from app.models.source import Source
from app.models.article import Article
from app.models.entity import Entity, EventEntity


@pytest.mark.asyncio
async def test_list_stories_api_empty(client: AsyncClient):
    response = await client.get("/api/v1/stories")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_and_get_story_api(client: AsyncClient, db_session: AsyncSession):
    domain = Domain(name="Trade", slug="trade-api")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Free Trade Agreements", slug="fta-api")
    db_session.add(topic)
    await db_session.flush()

    story = Story(
        topic_id=topic.id,
        title="India-EU FTA Negotiations 2026",
        slug="india-eu-fta-negotiations-2026",
        description="Comprehensive bilateral trade narrative between India and EU.",
        status="VERIFIED",
    )
    db_session.add(story)
    await db_session.flush()

    event = Event(
        canonical_title="India and EU conclude 12th round of trade talks in New Delhi",
        slug="india-eu-12th-round",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        grouping_status="GROUPED",
        verification_status="VERIFIED",
    )
    db_session.add(event)
    await db_session.flush()

    src = Source(name="The Hindu", domain="thehindu.com", rss_url="https://thehindu.com/rss", trust_score=0.95)
    db_session.add(src)
    await db_session.flush()

    art = Article(
        source_id=src.id,
        event_id=event.id,
        url="https://thehindu.com/trade-talks",
        headline="India EU trade talks conclude",
        hash="hash_trade_talks",
    )
    db_session.add(art)
    await db_session.commit()

    # Test GET /api/v1/stories
    res = await client.get("/api/v1/stories")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    matched = next((s for s in data if s["id"] == story.id), None)
    assert matched is not None
    assert matched["title"] == "India-EU FTA Negotiations 2026"
    assert matched["domain_name"] == "Trade"
    assert matched["topic_name"] == "Free Trade Agreements"
    assert matched["event_count"] == 1

    # Filter by topic_id
    res_filtered = await client.get(f"/api/v1/stories?topic_id={topic.id}")
    assert res_filtered.status_code == 200
    assert len(res_filtered.json()) >= 1

    # Filter by domain_id
    res_domain = await client.get(f"/api/v1/stories?domain_id={domain.id}")
    assert res_domain.status_code == 200
    assert len(res_domain.json()) >= 1

    # Test GET /api/v1/stories/{id}
    res_detail = await client.get(f"/api/v1/stories/{story.id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == story.id
    assert detail["title"] == story.title
    assert detail["status"] == "VERIFIED"
    assert len(detail["timeline"]) == 1
    assert detail["timeline"][0]["event_id"] == event.id
    assert "The Hindu" in detail["sources"]

    # Test 404 for invalid story id
    res_404 = await client.get("/api/v1/stories/non-existent-id")
    assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_trigger_cluster_api(client: AsyncClient, db_session: AsyncSession):
    domain = Domain(name="Parliament", slug="parliament-cluster-api")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Judicial Reforms", slug="judicial-reforms-api")
    db_session.add(topic)
    await db_session.flush()

    ev1 = Event(
        canonical_title="Supreme Court collegium recommends 5 new judges",
        slug="sc-collegium-recommends-judges",
        category="Parliament",
        domain_id=domain.id,
        topic_id=topic.id,
        grouping_status="UNGROUPED",
    )
    ev2 = Event(
        canonical_title="Law Ministry notifies appointment of 5 Supreme Court judges",
        slug="law-ministry-notifies-judges",
        category="Parliament",
        domain_id=domain.id,
        topic_id=topic.id,
        grouping_status="UNGROUPED",
    )
    db_session.add_all([ev1, ev2])
    await db_session.flush()

    ent = Entity(canonical_name="Supreme Court", type="Organisation")
    db_session.add(ent)
    await db_session.flush()

    db_session.add(EventEntity(event_id=ev1.id, entity_id=ent.id))
    db_session.add(EventEntity(event_id=ev2.id, entity_id=ent.id))
    await db_session.commit()

    # Trigger clustering endpoint
    cluster_res = await client.post("/api/v1/stories/cluster?limit=10")
    assert cluster_res.status_code == 200
    cluster_data = cluster_res.json()
    assert "grouped_count" in cluster_data
    assert "stories_created" in cluster_data
    assert cluster_data["grouped_count"] >= 2
    assert cluster_data["stories_created"] >= 1
