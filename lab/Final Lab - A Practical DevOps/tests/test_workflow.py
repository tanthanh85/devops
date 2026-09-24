def test_setup_is_one_time_and_login_works(client):
    assert client.get("/api/setup/status").get_json()["setup_required"] is True
    response=client.post("/api/setup/admin",json={"username":"admin","password":"correct-horse-battery"})
    assert response.status_code==201
    assert client.post("/api/setup/admin",json={"username":"other","password":"correct-horse-battery"}).status_code==409
    assert client.post("/api/session",json={"username":"admin","password":"correct-horse-battery"}).status_code==200


def test_setup_accepts_a_simple_password(client):
    response=client.post("/api/setup/admin",json={"username":"admin","password":"1"})
    assert response.status_code==201
    assert client.post("/api/session",json={"username":"admin","password":"1"}).status_code==200


def test_inventory_requires_authentication(client):
    assert client.get("/api/routers").status_code==401


def test_session_status_controls_authenticated_application(client):
    assert client.get("/api/session").get_json() == {"authenticated": False}
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    status = client.get("/api/session").get_json()
    assert status == {"authenticated": True, "username": "admin", "is_admin": True}
    client.delete("/api/session")
    assert client.get("/api/session").get_json() == {"authenticated": False}


def test_application_instance_is_visible(client):
    response=client.get("/api/instance")
    assert response.status_code==200
    assert response.get_json()["tier"]=="app"
    assert response.get_json()["instance"]


def test_netbox_inventory_sync_does_not_return_router_password(client, monkeypatch):
    client.post("/api/setup/admin",json={"username":"admin","password":"correct-horse-battery"})
    client.post("/api/session",json={"username":"admin","password":"correct-horse-battery"})
    monkeypatch.setattr("app.routes.fetch_devices", lambda *_: [{"name": "Learner Edge Router", "host": "192.0.2.10", "port": 443}])
    response=client.post("/api/inventory/netbox",json={"netbox_url":"https://netbox.test","netbox_api_token":"test-netbox-token"})
    assert response.status_code==200
    payload=client.get("/api/routers").get_json()
    assert "secret-value" not in str(payload)
    assert "password" not in str(payload)


def test_admin_can_supply_netbox_connection_for_one_inventory_request(client, monkeypatch):
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    captured = {}

    def fetch(url, token):
        captured.update(url=url, token=token)
        return [{"name": "Learner Router", "host": "192.0.2.10", "port": 443}]

    monkeypatch.setattr("app.routes.fetch_devices", fetch)
    response = client.post("/api/inventory/netbox", json={
        "netbox_url": "https://learner-netbox.test",
        "netbox_api_token": "nbt_key.secret",
    })
    assert response.status_code == 200
    assert captured == {"url": "https://learner-netbox.test", "token": "nbt_key.secret"}
    assert "nbt_key.secret" not in response.get_data(as_text=True)

    from app.models import NetBoxConfig
    from app.security import decrypt
    with client.application.app_context():
        config = client.application.extensions["sqlalchemy"].session.get(NetBoxConfig, 1)
        assert config.base_url == "https://learner-netbox.test"
        assert config.token_ciphertext != "nbt_key.secret"
        assert decrypt(config.token_ciphertext) == "nbt_key.secret"


def test_inventory_rejects_partial_learner_connection(client):
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    response = client.post("/api/inventory/netbox", json={"netbox_url": "https://learner-netbox.test"})
    assert response.status_code == 422


def test_trigger_pipeline_reads_loopback_intent_without_netbox_credentials(client, monkeypatch):
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    monkeypatch.setattr("app.routes.fetch_devices", lambda *_: [])
    client.post("/api/inventory/netbox", json={
        "netbox_url": "https://learner-netbox.test",
        "netbox_api_token": "nbt_key.secret",
    })
    monkeypatch.setattr("app.routes.fetch_loopbacks", lambda device, url, token: [{
        "name": "Loopback8", "ip": "192.0.2.8", "mask": "255.255.255.255",
    }])

    assert client.get("/api/internal/netbox/loopbacks?device=learner-router").status_code == 401
    response = client.get(
        "/api/internal/netbox/loopbacks?device=learner-router",
        headers={"X-Internal-Token": "test-secret"},
    )
    assert response.status_code == 200
    assert response.get_json() == {
        "netbox_device": "learner-router",
        "netbox_loopback_count": 1,
        "netbox_loopbacks": [{"name": "Loopback8", "ip": "192.0.2.8", "mask": "255.255.255.255"}],
    }


def test_manual_router_creation_is_not_available(client):
    client.post("/api/setup/admin",json={"username":"admin","password":"correct-horse-battery"})
    client.post("/api/session",json={"username":"admin","password":"correct-horse-battery"})
    assert client.post("/api/routers", json={"name": "manual-router"}).status_code == 405


def test_admin_configures_synthetic_account_and_results(client):
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    response = client.post("/api/synthetic/config", json={
        "username": "synthetic-user",
        "password": "synthetic-password",
        "interval_seconds": 30,
    })
    assert response.status_code == 200

    config = client.get(
        "/api/internal/synthetic/config",
        headers={"X-Synthetic-Token": "test-secret"},
    )
    assert config.status_code == 200
    assert config.get_json()["username"] == "synthetic-user"
    assert config.get_json()["password"] == "synthetic-password"
    assert config.get_json()["interval_seconds"] == 30

    recorded = client.post(
        "/api/internal/synthetic/results",
        headers={"X-Synthetic-Token": "test-secret"},
        json={"outcome": "success", "status_code": 200, "response_time_ms": 42.5},
    )
    assert recorded.status_code == 201
    dashboard = client.get("/api/synthetic/config").get_json()
    assert dashboard["last_result"]["outcome"] == "success"
    assert dashboard["last_result"]["response_time_ms"] == 42.5


def test_synthetic_interval_must_be_allowed(client):
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    response = client.post("/api/synthetic/config", json={
        "username": "synthetic-user",
        "password": "synthetic-password",
        "interval_seconds": 45,
    })
    assert response.status_code == 422


def test_authenticated_user_can_read_router_loopbacks(client, monkeypatch):
    client.post("/api/setup/admin", json={"username": "admin", "password": "admin-password"})
    client.post("/api/session", json={"username": "admin", "password": "admin-password"})
    monkeypatch.setattr("app.routes.fetch_devices", lambda *_: [{"name": "Learner Edge Router", "host": "192.0.2.10", "port": 443}])
    client.post("/api/inventory/netbox", json={"netbox_url":"https://netbox.test","netbox_api_token":"test-netbox-token"})
    router_id = client.get("/api/routers").get_json()["items"][0]["id"]
    monkeypatch.setattr("app.routes.collect_loopbacks", lambda router, password: [{
        "name": "Loopback108", "admin_status": "up", "protocol_status": "up",
        "ip": "192.0.2.108", "mask": "255.255.255.255",
    }])
    response = client.get(f"/api/routers/{router_id}/loopbacks")
    assert response.status_code == 200
    assert response.get_json()["items"][0]["name"] == "Loopback108"
    assert response.get_json()["items"][0]["mask"] == "255.255.255.255"
