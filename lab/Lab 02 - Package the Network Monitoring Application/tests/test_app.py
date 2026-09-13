import os

os.environ["MOCK_MODE"] = "true"
from app.app import app


def test_health():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_metrics_contract():
    response = app.test_client().get("/api/metrics")
    payload = response.get_json()
    assert response.status_code == 200
    assert 0 <= payload["cpu_percent"] <= 100
    assert 0 <= payload["memory_percent"] <= 100
    assert payload["timestamp"]
