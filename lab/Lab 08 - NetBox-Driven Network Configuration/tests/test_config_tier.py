import importlib.util
from pathlib import Path


def load_service(monkeypatch):
    monkeypatch.setenv("NETBOX_WEBHOOK_TOKEN", "shared-secret")
    monkeypatch.setenv("NETBOX_ROUTER_NAME", "Router 1")
    monkeypatch.setenv("GITLAB_PROJECT_ID", "123")
    monkeypatch.setenv("GITLAB_TRIGGER_TOKEN", "trigger-secret")
    path = Path(__file__).parents[1] / "config-tier" / "service.py"
    spec = importlib.util.spec_from_file_location("config_tier_service", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config.update(TESTING=True)
    return module


def valid_payload():
    return {
        "event": "created",
        "object_type": "ipam.ipaddress",
        "data": {
            "address": "192.0.2.108/32",
            "assigned_object": {"name": "Loopback108", "device": {"name": "Router 1"}},
        },
    }


def test_receiver_rejects_missing_shared_token(monkeypatch):
    service = load_service(monkeypatch)
    assert service.app.test_client().post("/webhooks/netbox", json=valid_payload()).status_code == 401


def test_receiver_triggers_only_valid_router_loopback(monkeypatch):
    service = load_service(monkeypatch)
    captured = {}

    class Response:
        def raise_for_status(self): pass
        def json(self): return {"id": 456}

    def post(url, data, timeout):
        captured.update(url=url, data=data, timeout=timeout)
        return Response()

    monkeypatch.setattr(service.requests, "post", post)
    response = service.app.test_client().post(
        "/webhooks/netbox", json=valid_payload(), headers={"X-NetBox-Webhook-Token": "shared-secret"},
    )
    assert response.status_code == 202
    assert response.get_json()["pipeline_id"] == 456
    assert captured["data"]["variables[NETBOX_ACTION]"] == "provision_loopback"
    assert captured["data"]["variables[LOOPBACK_NAME]"] == "Loopback108"


def test_receiver_ignores_non_32_address(monkeypatch):
    service = load_service(monkeypatch)
    payload = valid_payload(); payload["data"]["address"] = "192.0.2.1/24"
    response = service.app.test_client().post(
        "/webhooks/netbox", json=payload, headers={"X-NetBox-Webhook-Token": "shared-secret"},
    )
    assert response.status_code == 202
    assert response.get_json()["status"] == "ignored"
