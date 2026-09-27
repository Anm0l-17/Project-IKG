import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Domain
from app.models.topic import Topic
from app.models.event import Event
from app.services.search.hybrid_search import HybridSearchService
from app.ai.embeddings import embedding_service


@pytest.mark.asyncio
async def test_lexical_search_ranking(db_session: AsyncSession):
    domain = Domain(name="Economics", slug="economics-search")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Taxation", slug="taxation-search")
    db_session.add(topic)
    await db_session.flush()

    event1 = Event(
        canonical_title="GST Council slashes rates on cancer drugs and health insurance",
        slug="gst-council-rates-cancer-drugs",
        category="Economics",
        domain_id=domain.id,
        topic_id=topic.id,
        summary="GST Council announced a complete tax exemption for critical oncology medications in New Delhi.",
        grouping_status="UNGROUPED",
        verification_status="VERIFIED",
    )
    event2 = Event(
        canonical_title="Supreme Court delivers verdict on presidential power under Article 356",
        slug="sc-verdict-article-356",
        category="Parliament",
        domain_id=domain.id,
        topic_id=topic.id,
        summary="A constitution bench ruled on state emergency proclamations and governor roles.",
        grouping_status="UNGROUPED",
        verification_status="VERIFIED",
    )
    db_session.add_all([event1, event2])
    await db_session.commit()

    service = HybridSearchService(db_session)
    result = await service.search(query="cancer drugs GST Council", mode="lexical")

    assert result["total_results"] >= 1
    assert result["results"][0]["id"] == event1.id
    assert result["results"][0]["lexical_score"] > 0.3
    assert result["results"][0]["highlight_snippet"] is not None


@pytest.mark.asyncio
async def test_semantic_search_with_vectors(db_session: AsyncSession):
    domain = Domain(name="Defence", slug="defence-search")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Indigenisation", slug="indigenisation-search")
    db_session.add(topic)
    await db_session.flush()

    title1 = "Indian Navy commissions second nuclear-powered attack submarine"
    summary1 = "Submersible strategic naval deterrent constructed under Make in India defence initiative."
    vec1 = embedding_service.generate_embedding(f"{title1}. {summary1}")

    title2 = "Reserve Bank of India revises priority sector lending targets"
    summary2 = "Commercial banks must channel agricultural credit in rural districts."
    vec2 = embedding_service.generate_embedding(f"{title2}. {summary2}")

    event1 = Event(
        canonical_title=title1,
        slug="indian-navy-attack-sub",
        category="Defence",
        domain_id=domain.id,
        topic_id=topic.id,
        summary=summary1,
        embedding=vec1,
        verification_status="VERIFIED",
    )
    event2 = Event(
        canonical_title=title2,
        slug="rbi-lending-targets",
        category="Economics",
        domain_id=domain.id,
        topic_id=topic.id,
        summary=summary2,
        embedding=vec2,
        verification_status="VERIFIED",
    )
    db_session.add_all([event1, event2])
    await db_session.commit()

    service = HybridSearchService(db_session)
    result = await service.search(query="atomic naval submarine military fleet", mode="semantic")

    assert result["total_results"] >= 1
    top_result = result["results"][0]
    assert top_result["id"] == event1.id
    assert top_result["semantic_score"] > 0.4
    assert top_result["match_type"] == "SEMANTIC"


@pytest.mark.asyncio
async def test_hybrid_search_with_category_and_verification_filters(db_session: AsyncSession):
    domain = Domain(name="Trade", slug="trade-filters")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Bilateral Accords", slug="bilateral-accords")
    db_session.add(topic)
    await db_session.flush()

    ev_verified = Event(
        canonical_title="India and Singapore sign landmark digital cross-border trade agreement",
        slug="india-singapore-digital-trade",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        summary="Digital currency and fintech interoperability established.",
        verification_status="VERIFIED",
    )
    ev_developing = Event(
        canonical_title="India and UK hold trade talks on automobile tariffs",
        slug="india-uk-auto-tariffs",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
        summary="Negotiators discuss EV import taxes in London.",
        verification_status="DEVELOPING",
    )
    db_session.add_all([ev_verified, ev_developing])
    await db_session.commit()

    service = HybridSearchService(db_session)

    # Filter by VERIFIED only
    res_verified = await service.search(
        query="trade agreement",
        mode="hybrid",
        verification_status="VERIFIED",
    )
    assert all(r["verification_status"] == "VERIFIED" for r in res_verified["results"])
    assert any(r["id"] == ev_verified.id for r in res_verified["results"])
    assert not any(r["id"] == ev_developing.id for r in res_verified["results"])

    # Filter by category
    res_category = await service.search(
        query="trade",
        mode="hybrid",
        category="Trade",
    )
    assert len(res_category["results"]) >= 2
    assert all(r["category"] == "Trade" for r in res_category["results"])


@pytest.mark.asyncio
async def test_backfill_event_embeddings(db_session: AsyncSession):
    domain = Domain(name="Parliament", slug="parliament-backfill")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Legislation", slug="legislation-backfill")
    db_session.add(topic)
    await db_session.flush()

    event = Event(
        canonical_title="Lok Sabha passes Telecommunications Regulatory Amendment Bill",
        slug="telecom-bill-passed",
        category="Parliament",
        domain_id=domain.id,
        topic_id=topic.id,
        summary="The legislation modernizes spectrum allocation and spectrum auctions.",
        embedding=None,  # Null embedding initially
    )
    db_session.add(event)
    await db_session.commit()

    service = HybridSearchService(db_session)
    count = await service.backfill_event_embeddings(batch_size=10)

    assert count >= 1
    await db_session.refresh(event)
    assert event.embedding is not None
    assert len(event.embedding) == 384
