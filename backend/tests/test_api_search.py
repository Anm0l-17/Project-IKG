import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Domain
from app.models.topic import Topic
from app.models.event import Event


@pytest.mark.asyncio
async def test_search_api_empty_query(client: AsyncClient):
    response = await client.get("/api/v1/search?q=")
    # FastAPI returns 422 because min_length=1
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_search_api_hybrid_mode(client: AsyncClient, db_session: AsyncSession):
    domain = Domain(name="Geopolitics", slug="geopolitics-api-search")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Multilateral Summits", slug="summits-api-search")
    db_session.add(topic)
    await db_session.flush()

    event = Event(
        canonical_title="India hosts Quad Foreign Ministers Meeting in New Delhi",
        slug="quad-foreign-ministers-delhi",
        category="Geopolitics",
        domain_id=domain.id,
        topic_id=topic.id,
        summary="Leaders discussed maritime security in the Indo-Pacific and supply chain resilience.",
        verification_status="VERIFIED",
    )
    db_session.add(event)
    await db_session.commit()

    # Test Hybrid mode
    res = await client.get("/api/v1/search?q=Quad+Indo-Pacific+security&mode=hybrid")
    assert res.status_code == 200
    data = res.json()
    assert data["query"] == "Quad Indo-Pacific security"
    assert data["mode"] == "hybrid"
    assert data["total_results"] >= 1
    assert data["results"][0]["id"] == event.id
    assert "relevance_score" in data["results"][0]
    assert "semantic_score" in data["results"][0]
    assert "lexical_score" in data["results"][0]


@pytest.mark.asyncio
async def test_search_api_filters(client: AsyncClient, db_session: AsyncSession):
    domain = Domain(name="Defence", slug="defence-api-search")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Missile Tech", slug="missile-tech-api")
    db_session.add(topic)
    await db_session.flush()

    ev1 = Event(
        canonical_title="DRDO tests Agni-Prime ballistic missile off Odisha coast",
        slug="drdo-tests-agni-prime-api",
        category="Defence",
        domain_id=domain.id,
        topic_id=topic.id,
        verification_status="VERIFIED",
    )
    ev2 = Event(
        canonical_title="Finance Ministry reviews defence expenditure for FY26",
        slug="finmin-defence-expenditure-api",
        category="Economics",
        domain_id=domain.id,
        topic_id=topic.id,
        verification_status="VERIFIED",
    )
    db_session.add_all([ev1, ev2])
    await db_session.commit()

    # Search with category=Defence
    res = await client.get("/api/v1/search?q=defence&category=Defence")
    assert res.status_code == 200
    data = res.json()
    assert all(r["category"] == "Defence" for r in data["results"])


@pytest.mark.asyncio
async def test_backfill_embeddings_api(client: AsyncClient, db_session: AsyncSession):
    res = await client.post("/api/v1/search/backfill-embeddings?batch_size=50")
    assert res.status_code == 200
    data = res.json()
    assert "updated_count" in data
    assert "message" in data
