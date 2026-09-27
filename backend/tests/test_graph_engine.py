import pytest
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.domain import Domain
from app.models.topic import Topic
from app.models.story import Story
from app.models.event import Event
from app.models.entity import Entity, EventEntity
from app.models.relationship import EventRelationship
from app.services.graph.engine import GraphEngine


@pytest.mark.asyncio
async def test_precedes_inference_within_same_story(db_session: AsyncSession):
    # Setup Domain, Topic, Story
    domain = Domain(name="Trade Policy", slug="trade-policy")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="India-UK FTA", slug="india-uk-fta")
    db_session.add(topic)
    await db_session.flush()

    story = Story(topic_id=topic.id, title="India-UK Trade Talks 2026", slug="india-uk-talks-2026")
    db_session.add(story)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    event1 = Event(
        canonical_title="India and UK commence Round 14 of FTA negotiations",
        slug="india-uk-round-14",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        first_seen=now - timedelta(days=5),
        last_updated=now - timedelta(days=5),
    )
    event2 = Event(
        canonical_title="India and UK finalize agreement on duty concessions",
        slug="india-uk-finalize-concessions",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        primary_story_id=story.id,
        first_seen=now - timedelta(days=1),
        last_updated=now - timedelta(days=1),
    )
    db_session.add_all([event1, event2])
    await db_session.commit()

    engine = GraphEngine(db_session)
    inferred = await engine.infer_relationships_for_event(event2.id)

    assert len(inferred) >= 1
    precedes_rel = next((r for r in inferred if r.relationship_type == "PRECEDES"), None)
    assert precedes_rel is not None
    assert precedes_rel.source_event_id == event1.id
    assert precedes_rel.target_event_id == event2.id
    assert precedes_rel.confidence >= 0.90
    assert "Temporal sequence within Story" in precedes_rel.reasoning


@pytest.mark.asyncio
async def test_causes_inference_with_causal_cue_and_entity_overlap(db_session: AsyncSession):
    domain = Domain(name="Economics", slug="economics")
    db_session.add(domain)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    event1 = Event(
        canonical_title="RBI raises repo rate by 25 bps to curb inflation",
        slug="rbi-raises-repo-rate-25bps",
        category="Economics",
        domain_id=domain.id,
        first_seen=now - timedelta(days=3),
        last_updated=now - timedelta(days=3),
        summary="Reserve Bank of India Monetary Policy Committee decided to hike rates.",
    )
    event2 = Event(
        canonical_title="Commercial banks hike home loan interest rates as a direct result of RBI rate hike",
        slug="banks-hike-lending-rates",
        category="Economics",
        domain_id=domain.id,
        first_seen=now - timedelta(days=1),
        last_updated=now - timedelta(days=1),
        summary="As a direct result of RBI rate adjustment, commercial lenders revised lending benchmarks.",
    )
    db_session.add_all([event1, event2])
    await db_session.flush()

    # Add shared entities
    entity_rbi = Entity(canonical_name="Reserve Bank of India", type="Organisation")
    entity_rate = Entity(canonical_name="Repo Rate", type="Policy")
    db_session.add_all([entity_rbi, entity_rate])
    await db_session.flush()

    ee1_1 = EventEntity(event_id=event1.id, entity_id=entity_rbi.id)
    ee1_2 = EventEntity(event_id=event1.id, entity_id=entity_rate.id)
    ee2_1 = EventEntity(event_id=event2.id, entity_id=entity_rbi.id)
    ee2_2 = EventEntity(event_id=event2.id, entity_id=entity_rate.id)
    db_session.add_all([ee1_1, ee1_2, ee2_1, ee2_2])
    await db_session.commit()

    engine = GraphEngine(db_session)
    inferred = await engine.infer_relationships_for_event(event2.id)

    causes_rel = next((r for r in inferred if r.relationship_type == "CAUSES"), None)
    assert causes_rel is not None
    assert causes_rel.source_event_id == event1.id
    assert causes_rel.target_event_id == event2.id
    assert causes_rel.confidence >= 0.70
    assert "Causal inference" in causes_rel.reasoning


@pytest.mark.asyncio
async def test_related_to_inference_with_shared_entities(db_session: AsyncSession):
    domain = Domain(name="Defence", slug="defence")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Indigenous Defence Systems", slug="indigenous-defence")
    db_session.add(topic)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    event1 = Event(
        canonical_title="DRDO tests next-generation air defence missile",
        slug="drdo-tests-missile",
        category="Defence",
        domain_id=domain.id,
        topic_id=topic.id,
        first_seen=now - timedelta(days=2),
        last_updated=now - timedelta(days=2),
    )
    event2 = Event(
        canonical_title="Ministry of Defence places order for DRDO air defence batteries",
        slug="mod-orders-missile-batteries",
        category="Defence",
        domain_id=domain.id,
        topic_id=topic.id,
        first_seen=now - timedelta(days=1),
        last_updated=now - timedelta(days=1),
    )
    db_session.add_all([event1, event2])
    await db_session.flush()

    # Add 3 shared entities
    ent1 = Entity(canonical_name="DRDO", type="Organisation")
    ent2 = Entity(canonical_name="Ministry of Defence", type="Ministry")
    ent3 = Entity(canonical_name="Indian Air Force", type="Military")
    db_session.add_all([ent1, ent2, ent3])
    await db_session.flush()

    for ent in [ent1, ent2, ent3]:
        db_session.add(EventEntity(event_id=event1.id, entity_id=ent.id))
        db_session.add(EventEntity(event_id=event2.id, entity_id=ent.id))
    await db_session.commit()

    engine = GraphEngine(db_session)
    inferred = await engine.infer_relationships_for_event(event2.id)

    related_rel = next((r for r in inferred if r.relationship_type == "RELATED_TO"), None)
    assert related_rel is not None
    assert related_rel.confidence >= 0.70
    assert "Topical affinity" in related_rel.reasoning


@pytest.mark.asyncio
async def test_subgraph_extraction(db_session: AsyncSession):
    domain = Domain(name="Current Affairs", slug="current-affairs")
    db_session.add(domain)
    await db_session.flush()

    event = Event(
        canonical_title="New Digital Personal Data Protection Rules notified",
        slug="dpdp-rules-notified",
        category="Current Affairs",
        domain_id=domain.id,
    )
    db_session.add(event)
    await db_session.flush()

    entity = Entity(canonical_name="MeitY", type="Ministry")
    db_session.add(entity)
    await db_session.flush()

    ee = EventEntity(event_id=event.id, entity_id=entity.id, relationship_type="MENTIONS", confidence=0.98)
    db_session.add(ee)
    await db_session.commit()

    engine = GraphEngine(db_session)
    subgraph = await engine.get_event_subgraph(event.id)

    assert subgraph is not None
    assert subgraph["central_event_id"] == event.id
    assert subgraph["node_count"] == 2  # 1 event node + 1 entity node
    assert subgraph["edge_count"] == 1  # 1 event-to-entity edge

    event_node = next((n for n in subgraph["nodes"] if n["type"] == "EVENT"), None)
    assert event_node is not None
    assert event_node["is_central"] is True

    entity_node = next((n for n in subgraph["nodes"] if n["type"] == "ENTITY"), None)
    assert entity_node is not None
    assert entity_node["label"] == "MeitY"
