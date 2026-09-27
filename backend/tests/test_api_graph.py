import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Domain
from app.models.event import Event
from app.models.entity import Entity, EventEntity


@pytest.mark.asyncio
async def test_get_global_graph_empty(client: AsyncClient):
    response = await client.get("/api/v1/graph")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert data["node_count"] == 0


@pytest.mark.asyncio
async def test_get_event_subgraph_api(client: AsyncClient, db_session: AsyncSession):
    domain = Domain(name="Geopolitics", slug="geopolitics")
    db_session.add(domain)
    await db_session.flush()

    event = Event(
        canonical_title="India chairs Voice of Global South Summit 2026",
        slug="global-south-summit-2026",
        category="Geopolitics",
        domain_id=domain.id,
    )
    db_session.add(event)
    await db_session.flush()

    entity = Entity(canonical_name="Global South", type="Concept")
    db_session.add(entity)
    await db_session.flush()

    ee = EventEntity(event_id=event.id, entity_id=entity.id, relationship_type="MENTIONS", confidence=0.95)
    db_session.add(ee)
    await db_session.commit()

    # Test /api/v1/graph/event/{id}
    res = await client.get(f"/api/v1/graph/event/{event.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["central_event_id"] == event.id
    assert data["node_count"] == 2
    assert data["edge_count"] == 1

    # Test alias /api/v1/events/{id}/graph
    alias_res = await client.get(f"/api/v1/events/{event.id}/graph")
    assert alias_res.status_code == 200
    alias_data = alias_res.json()
    assert alias_data["central_event_id"] == event.id


@pytest.mark.asyncio
async def test_infer_relationships_api(client: AsyncClient, db_session: AsyncSession):
    domain = Domain(name="Parliament", slug="parliament")
    db_session.add(domain)
    await db_session.flush()

    event = Event(
        canonical_title="Lok Sabha passes Finance Bill 2026",
        slug="lok-sabha-passes-finance-bill-2026",
        category="Parliament",
        domain_id=domain.id,
    )
    db_session.add(event)
    await db_session.commit()

    res = await client.post(f"/api/v1/graph/infer/{event.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["event_id"] == event.id
    assert "inferred_relationships_count" in data
