import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_events_api(client: AsyncClient):
    response = await client.get("/api/v1/events")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_events_invalid_status_filter(client: AsyncClient):
    response = await client.get("/api/v1/events?verification_status=INVALID_STATUS")
    assert response.status_code == 400
    assert "Invalid verification_status" in response.json()["detail"]


from unittest.mock import patch


@pytest.mark.asyncio
async def test_trigger_ingestion_background_api(client: AsyncClient):
    with patch("app.api.v1.event._execute_ingestion_pipeline"):
        response = await client.post("/api/v1/events/ingest")
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "PENDING"
        assert "triggered successfully" in data["message"]
