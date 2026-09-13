from unittest.mock import Mock, patch


def test_loopback_api_returns_read_only_netbox_view(client):
    client.post("/api/setup/admin", json={"username":"admin","password":"correct-horse-battery"})
    client.post("/api/session", json={"username":"admin","password":"correct-horse-battery"})
    expected=[{"device":"router-1","interface":"Loopback100","enabled":True,"addresses":["192.0.2.100/32"]}]
    with patch("app.loopbacks.list_loopbacks", return_value=expected):
        response=client.get("/api/loopbacks")
    assert response.status_code == 200
    assert response.get_json()["items"] == expected

