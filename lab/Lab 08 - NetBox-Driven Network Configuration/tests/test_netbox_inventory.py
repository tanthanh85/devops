from app.netbox_client import fetch_devices


def test_netbox_device_inventory_extracts_management_fields(client, monkeypatch):
    class Response:
        def raise_for_status(self): pass
        def json(self):
            return {"results": [{
                "name": "Router 1",
                "primary_ip4": {"address": "192.0.2.10/24"},
                "custom_fields": {"restconf_port": 8443},
            }]}

    captured = {}

    def get(url, **kwargs):
        captured.update(url=url, kwargs=kwargs)
        return Response()

    monkeypatch.setattr("app.netbox_client.requests.get", get)
    with client.application.app_context():
        devices = fetch_devices()
    assert devices == [{"name": "Router 1", "host": "192.0.2.10", "port": 8443}]
    assert captured["url"].endswith("/api/dcim/devices/")
    assert captured["kwargs"]["params"] == {"status": "active", "limit": 0}
