def test_setup_is_one_time_and_login_works(client):
    assert client.get("/api/setup/status").get_json()["setup_required"] is True
    response=client.post("/api/setup/admin",json={"username":"admin","password":"correct-horse-battery"})
    assert response.status_code==201
    assert client.post("/api/setup/admin",json={"username":"other","password":"correct-horse-battery"}).status_code==409
    assert client.post("/api/session",json={"username":"admin","password":"correct-horse-battery"}).status_code==200


def test_inventory_requires_authentication(client):
    assert client.get("/api/routers").status_code==401


def test_router_password_is_not_returned(client):
    client.post("/api/setup/admin",json={"username":"admin","password":"correct-horse-battery"})
    client.post("/api/session",json={"username":"admin","password":"correct-horse-battery"})
    response=client.post("/api/routers",json={"name":"router-1","host":"192.0.2.10","port":443,"username":"student","password":"secret-value"})
    assert response.status_code==201
    payload=client.get("/api/routers").get_json()
    assert "secret-value" not in str(payload)
    assert "password" not in str(payload)
