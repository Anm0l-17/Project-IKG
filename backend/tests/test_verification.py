from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.enums import EventLifecycleState, VerificationStatus
from app.models.event import Event
from app.models.source import Source
from app.models.verification import Verification, Vote
from app.services.events.candidate_generation import CandidateEventService
from app.services.events.verification import VerificationEngine


@pytest.mark.asyncio
async def test_single_source_creates_pending_verification_with_one_vote(
    db_session: AsyncSession,
):
    source = Source(name="GKToday", domain="gktoday.in")
    db_session.add(source)
    await db_session.commit()

    article = Article(
        source_id=source.id,
        url="https://gktoday.in/art1",
        headline="Cabinet approves new Semiconductor Mission",
        summary="India Cabinet has approved a major semiconductor scheme.",
        published_at=datetime.now(UTC),
        scraped_at=datetime.now(UTC),
        clean_text="Clean content",
        hash="hash_semi_1",
    )
    db_session.add(article)
    await db_session.commit()

    candidate_service = CandidateEventService(db_session)
    events = await candidate_service.generate_candidates_from_articles([article])

    assert len(events) == 1
    event = events[0]

    assert event.verification_status == VerificationStatus.PENDING.value
    assert event.status == EventLifecycleState.PENDING.value

    # Check Verification record
    stmt = select(Verification).where(Verification.event_id == event.id)
    res = await db_session.execute(stmt)
    ver = res.scalar_one_or_none()

    assert ver is not None
    assert ver.vote_count == 1
    assert ver.required_votes == 2
    assert ver.status == VerificationStatus.PENDING.value

    # Check Vote record
    vote_stmt = select(Vote).where(Vote.verification_id == ver.id)
    vote_res = await db_session.execute(vote_stmt)
    votes = vote_res.scalars().all()
    assert len(votes) == 1
    assert votes[0].source_id == source.id


@pytest.mark.asyncio
async def test_corroborating_source_promotes_event_to_verified(
    db_session: AsyncSession,
):
    source1 = Source(name="GKToday", domain="gktoday.in")
    source2 = Source(name="The Hindu", domain="thehindu.com")
    db_session.add_all([source1, source2])
    await db_session.commit()

    article1 = Article(
        source_id=source1.id,
        url="https://gktoday.in/art1",
        headline="Cabinet approves new Semiconductor Mission",
        summary="Summary 1",
        published_at=datetime.now(UTC),
        scraped_at=datetime.now(UTC),
        clean_text="Clean text 1",
        hash="hash_semi_1",
    )
    db_session.add(article1)
    await db_session.commit()

    candidate_service = CandidateEventService(db_session)
    events1 = await candidate_service.generate_candidates_from_articles([article1])
    event = events1[0]
    assert event.verification_status == VerificationStatus.PENDING.value

    # Second article from The Hindu describing the same event
    article2 = Article(
        source_id=source2.id,
        url="https://thehindu.com/art2",
        headline="Cabinet approves new Semiconductor Mission",
        summary="Summary 2",
        published_at=datetime.now(UTC),
        scraped_at=datetime.now(UTC),
        clean_text="Clean text 2",
        hash="hash_semi_2",
    )
    db_session.add(article2)
    await db_session.commit()

    # Pass 2nd article into candidate generation
    events2 = await candidate_service.generate_candidates_from_articles([article2])

    # No new event should be created; existing event should be promoted!
    assert len(events2) == 0

    await db_session.refresh(event)
    assert event.verification_status == VerificationStatus.VERIFIED.value
    assert event.status == EventLifecycleState.VERIFIED.value

    # Check verification vote_count
    stmt = select(Verification).where(Verification.event_id == event.id)
    res = await db_session.execute(stmt)
    ver = res.scalar_one()
    assert ver.vote_count == 2
    assert ver.status == VerificationStatus.VERIFIED.value


@pytest.mark.asyncio
async def test_10_day_pending_queue_expiry(db_session: AsyncSession):
    source = Source(name="Test Source", domain="test.com")
    db_session.add(source)
    await db_session.commit()

    # Create event with verification created 11 days ago
    eleven_days_ago = datetime.now(UTC) - timedelta(days=11)

    event = Event(
        canonical_title="Stale Event Headline",
        slug="stale-event-headline",
        category="Current Affairs",
        verification_status=VerificationStatus.PENDING.value,
        status=EventLifecycleState.PENDING.value,
        created_at=eleven_days_ago,
    )
    db_session.add(event)
    await db_session.flush()

    verification = Verification(
        event_id=event.id,
        vote_count=1,
        required_votes=2,
        status=VerificationStatus.PENDING.value,
        expires_at=eleven_days_ago + timedelta(days=10),  # Expired 1 day ago
    )
    db_session.add(verification)
    await db_session.commit()

    v_engine = VerificationEngine(db_session)
    expired_count = await v_engine.process_pending_queue_expirations()

    assert expired_count == 1
    await db_session.refresh(event)
    await db_session.refresh(verification)

    assert event.verification_status == VerificationStatus.ARCHIVED.value
    assert event.status == EventLifecycleState.ARCHIVED.value
    assert verification.status == VerificationStatus.ARCHIVED.value
