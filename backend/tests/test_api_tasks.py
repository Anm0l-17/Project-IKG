import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_tasks_status_api(client: AsyncClient):
    response = await client.get("/api/v1/tasks/status")
    assert response.status_code == 200
    data = response.json()
    assert "queue_status" in data
    assert "distributed_queue" in data
    assert "backend" in data


@pytest.mark.asyncio
async def test_trigger_task_api_valid(client: AsyncClient):
    payload = {
        "task_name": "verification_pass",
    }
    response = await client.post("/api/v1/tasks/trigger", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("DISPATCHED_IN_PROCESS", "ENQUEUED_DISTRIBUTED")
    assert data["task_name"] == "task_verification_consensus"
    assert "job_id" in data


@pytest.mark.asyncio
async def test_trigger_task_api_invalid(client: AsyncClient):
    payload = {
        "task_name": "non_existent_job",
    }
    response = await client.post("/api/v1/tasks/trigger", json=payload)
    assert response.status_code == 400
    assert "Unknown task" in response.json()["detail"]
