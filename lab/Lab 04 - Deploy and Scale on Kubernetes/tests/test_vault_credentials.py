from unittest.mock import patch

from app.vault_client import RouterRecord


def authenticated(client):
    client.post("/api/setup/admin", json={"username":"admin","password":"correct-horse-battery"})
    client.post("/api/session", json={"username":"admin","password":"correct-horse-battery"})


def test_inventory_is_read_from_vault(client):
    authenticated(client)
    items = [{"name":"router-1","host":"192.0.2.10","port":443,"enabled":True,"credential_source":"vault"}]
    with patch("app.routes.vault_list_routers", return_value=items):
        response = client.get("/api/routers")
    assert response.status_code == 200
    assert response.get_json()["items"] == items


def test_metric_collection_uses_complete_vault_record(client):
    authenticated(client)
    router=RouterRecord("router-1","192.0.2.10",443,"vault-user","vault-pass",None,True)
    with patch("app.routes.read_router", return_value=router) as vault_read, patch("app.routes.collect", return_value={"cpu_percent":12.5,"memory_percent":40.0}) as collect:
        response=client.get("/api/routers/router-1/metrics")
    assert response.status_code == 200
    vault_read.assert_called_once_with("router-1")
    collect.assert_called_once_with(router)


def test_inventory_mutation_api_is_not_available(client):
    authenticated(client)
    assert client.post("/api/routers", json={}).status_code == 405
