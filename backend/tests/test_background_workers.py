import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import Domain
from app.models.event import Event
from app.models.topic import Topic
from app.workers.dispatcher import TaskDispatcher
from app.workers.tasks import (
    task_backfill_embeddings,
    task_infer_relationships,
    task_verification_consensus,
)


@pytest.mark.asyncio
async def test_task_dispatcher_in_process_fallback():
    dispatcher = TaskDispatcher()

    executed = False

    async def dummy_task(arg1: str):
        nonlocal executed
        executed = True
        return f"done_{arg1}"

    result = await dispatcher.enqueue("dummy_task", dummy_task, "test_val")
    assert result["status"] in ("DISPATCHED_IN_PROCESS", "ENQUEUED_DISTRIBUTED")
    assert "dummy_task" in result["task_name"]
    assert "job_id" in result

    health = await dispatcher.health_check()
    assert "status" in health
    assert "backend" in health


@pytest.mark.asyncio
async def test_task_infer_relationships_execution(db_session: AsyncSession):
    domain = Domain(name="Trade", slug="trade-tasks-bg")
    db_session.add(domain)
    await db_session.flush()

    topic = Topic(domain_id=domain.id, name="Logistics", slug="logistics-tasks-bg")
    db_session.add(topic)
    await db_session.flush()

    event = Event(
        canonical_title="PM Gati Shakti national master plan completes 4 years",
        slug="gati-shakti-4-years",
        category="Trade",
        domain_id=domain.id,
        topic_id=topic.id,
    )
    db_session.add(event)
    await db_session.commit()

    # Empty event id returns 0
    res_empty = await task_infer_relationships(None, event_id="")
    assert res_empty["relationships_created"] == 0

    # Execute for created event
    res = await task_infer_relationships(None, event_id=event.id)
    assert res["event_id"] == event.id
    assert "relationships_created" in res


@pytest.mark.asyncio
async def test_task_verification_and_backfill_runs(db_session: AsyncSession):
    v_res = await task_verification_consensus(None)
    assert "expired_events_count" in v_res

    b_res = await task_backfill_embeddings(None, batch_size=10)
    assert "embeddings_backfilled" in b_res
