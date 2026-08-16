from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify health probe endpoint returns 200 OK."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "database" in response.json()

def test_dashboard_stats():
    """Verify stats endpoint returns required data structure."""
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_tickets" in data
    assert "by_status" in data
