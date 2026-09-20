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


def test_application_instance_is_visible(client):
    response=client.get("/api/instance")
    assert response.status_code==200
    assert response.get_json()["tier"]=="app"
    assert response.get_json()["instance"]


def test_router_password_is_not_returned(client):
    client.post("/api/setup/admin",json={"username":"admin","password":"correct-horse-battery"})
    client.post("/api/session",json={"username":"admin","password":"correct-horse-battery"})
    response=client.post("/api/routers",json={"name":"router-1","host":"192.0.2.10","port":443,"username":"student","password":"secret-value"})
    assert response.status_code==201
    payload=client.get("/api/routers").get_json()
    assert "secret-value" not in str(payload)
    assert "password" not in str(payload)


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
