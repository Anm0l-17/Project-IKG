import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_observability_and_security_headers(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200

    # Observability headers
    assert "x-request-id" in response.headers
    assert "x-response-time-ms" in response.headers

    # Security headers
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert "x-xss-protection" in response.headers


@pytest.mark.asyncio
async def test_readiness_probe_api(client: AsyncClient):
    response = await client.get("/api/v1/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ready", "degraded")
    assert "database" in data
    assert "task_queue" in data


@pytest.mark.asyncio
async def test_metrics_api(client: AsyncClient):
    response = await client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "telemetry" in data
    assert "platform_stats" in data
    assert data["telemetry"]["total_requests"] >= 1
    assert "total_events" in data["platform_stats"]
    assert "verified_events" in data["platform_stats"]
    assert "total_stories" in data["platform_stats"]
