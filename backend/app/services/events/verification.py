import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.article import Article
from app.models.enums import EventLifecycleState, EvidenceType, VerificationStatus
from app.models.event import Event
from app.models.evidence import Evidence
from app.models.verification import Verification, Vote

logger = logging.getLogger(__name__)


class VerificationEngine:
    """
    Core Verification Engine implementing the 2/3 multi-source voting rule
    and 10-day pending queue lifecycle manager.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initialize_verification_for_event(
        self, event: Event, article: Article
    ) -> Verification:
        """
        Initializes a Verification record and casts the 1st vote for the initial source.
        """
        expires_at = datetime.now(UTC) + timedelta(days=10)

        verification = Verification(
            event_id=event.id,
            vote_count=1,
            required_votes=2,
            confidence=0.5,
            status=VerificationStatus.PENDING.value,
            expires_at=expires_at,
        )
        self.db.add(verification)
        await self.db.flush()

        vote = Vote(
            verification_id=verification.id,
            source_id=article.source_id,
            article_id=article.id,
            decision="MATCHED",
            reason="Primary publication candidate event discovery.",
            confidence=1.0,
        )
        self.db.add(vote)
        await self.db.flush()

        return verification

    async def evaluate_incoming_article_against_pending_events(
        self, article: Article
    ) -> bool:
        """
        Checks if an incoming article corroborates an existing PENDING event from a different source.
        If corroboration is confirmed, registers a new Vote and promotes the event if vote_count >= 2.
        """
        # Fetch PENDING events from the last 10 days
        stmt = (
            select(Event)
            .where(
                Event.verification_status == VerificationStatus.PENDING.value,
                Event.created_at >= datetime.now(UTC) - timedelta(days=10),
            )
            .order_by(Event.created_at.desc())
            .limit(200)
        )
        res = await self.db.execute(stmt)
        pending_events = res.scalars().all()

        if not pending_events:
            return False

        # Execute 2-Stage Candidate Matching Cascade
        from app.ai.matching import candidate_matching_service

        match_result = candidate_matching_service.match_article_to_events(
            article, pending_events
        )

        if match_result.is_match and match_result.event:
            event = match_result.event
            await self.db.refresh(event, ["verification"])
            verification = event.verification

            if not verification:
                verification = await self.initialize_verification_for_event(
                    event, article
                )
                return True

            # Check if this source has already voted
            vote_stmt = select(Vote).where(
                Vote.verification_id == verification.id,
                Vote.source_id == article.source_id,
            )
            vote_res = await self.db.execute(vote_stmt)
            existing_vote = vote_res.scalar_one_or_none()

            if existing_vote:
                return False  # 1 vote per publication rule

            # Add new Vote
            new_vote = Vote(
                verification_id=verification.id,
                source_id=article.source_id,
                article_id=article.id,
                decision="MATCHED",
                reason=f"Corroboration vote via {match_result.stage} (Score: {match_result.similarity_score:.2f}).",
                confidence=match_result.similarity_score,
            )
            self.db.add(new_vote)

            # Add Evidence record
            evidence = Evidence(
                article_id=article.id,
                event_id=event.id,
                evidence_type=EvidenceType.EVENT_EXISTENCE.value,
                confidence=match_result.similarity_score,
                reasoning=f"Corroborating source evidence via {match_result.stage}.",
            )
            self.db.add(evidence)

            verification.vote_count += 1
            verification.confidence = min(
                1.0, verification.vote_count / verification.required_votes
            )

            # 2/3 Voting Consensus Rule Promotion
            if verification.vote_count >= verification.required_votes:
                verification.status = VerificationStatus.VERIFIED.value
                verification.verified_at = datetime.now(UTC)

                event.verification_status = VerificationStatus.VERIFIED.value
                event.status = EventLifecycleState.VERIFIED.value
                logger.info(
                    f"Event {event.id} PROMOTED to VERIFIED ({verification.vote_count}/{verification.required_votes} votes)"
                )

            await self.db.commit()
            return True

        return False

    async def process_pending_queue_expirations(self) -> int:
        """
        Scans PENDING events exceeding the 10-day window and transitions them to ARCHIVED.
        """
        now = datetime.now(UTC)
        stmt = select(Verification).where(
            Verification.status == VerificationStatus.PENDING.value,
            Verification.expires_at <= now,
        )
        res = await self.db.execute(stmt)
        expired_verifications = res.scalars().all()

        expired_count = 0
        for ver in expired_verifications:
            ver.status = VerificationStatus.ARCHIVED.value

            # Update corresponding Event
            event_stmt = select(Event).where(Event.id == ver.event_id)
            event_res = await self.db.execute(event_stmt)
            event = event_res.scalar_one_or_none()

            if event:
                event.verification_status = VerificationStatus.ARCHIVED.value
                event.status = EventLifecycleState.ARCHIVED.value
                expired_count += 1

        if expired_count > 0:
            await self.db.commit()
            logger.info(
                f"Expired {expired_count} uncorroborated single-source events to ARCHIVED"
            )

        return expired_count
