import importlib


def make_client(monkeypatch):
    monkeypatch.setenv("WEBHOOK_TOKEN", "test-token-value")
    module = importlib.import_module("app")
    module.events.clear()
    module.app.config.update(TESTING=True)
    return module.app.test_client()


def test_rejects_missing_token(monkeypatch):
    client = make_client(monkeypatch)
    assert client.post("/webhook/elastic", json={"rule_name": "test"}).status_code == 401


def test_accepts_and_lists_sanitized_event(monkeypatch):
    client = make_client(monkeypatch)
    response = client.post(
        "/webhook/elastic",
        headers={"X-Webhook-Token": "test-token-value"},
        json={"rule_name": "High latency", "status": "active", "value": 4100, "threshold": 3000},
    )
    assert response.status_code == 202
    item = client.get("/api/events").get_json()["items"][0]
    assert item["rule_name"] == "High latency"
    assert item["value"] == 4100

