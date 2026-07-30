import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_categories_endpoint():
    response = client.get("/api/v1/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) == 6
    category_names = [c["name"] for c in categories]
    assert "Parliament" in category_names
    assert "Economics" in category_names
    assert "Defence" in category_names
