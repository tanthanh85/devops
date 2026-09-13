from __future__ import annotations

import hvac
from flask import current_app
import requests


def _vault_client():
    client = hvac.Client(url=current_app.config["VAULT_ADDR"], timeout=5)
    with open(current_app.config["KUBERNETES_TOKEN_PATH"], encoding="utf-8") as handle:
        jwt = handle.read().strip()
    response = client.auth.kubernetes.login(role=current_app.config["VAULT_KUBERNETES_ROLE"], jwt=jwt)
    client.token = response["auth"]["client_token"]
    return client


def _netbox_session():
    secret = _vault_client().secrets.kv.v2.read_secret_version(
        mount_point=current_app.config["VAULT_KV_MOUNT"], path="integrations/netbox"
    )["data"]["data"]
    base_url = str(secret["url"]).rstrip("/")
    session = requests.Session()
    session.headers.update({"Authorization": f"Token {secret['token']}", "Accept": "application/json"})
    session.verify = secret.get("verify_tls", True)
    return base_url, session


def list_loopbacks():
    base_url, session = _netbox_session()
    response = session.get(f"{base_url}/api/dcim/interfaces/", params={"limit": 200}, timeout=10)
    response.raise_for_status()
    loopbacks = []
    for interface in response.json().get("results", []):
        if not str(interface.get("name", "")).lower().startswith("loopback"):
            continue
        addresses = session.get(f"{base_url}/api/ipam/ip-addresses/", params={"interface_id": interface["id"], "limit": 50}, timeout=10)
        addresses.raise_for_status()
        device = interface.get("device") or {}
        loopbacks.append({"device": device.get("name") or device.get("display"), "interface": interface["name"], "enabled": interface.get("enabled", True), "addresses": [item["address"] for item in addresses.json().get("results", [])]})
    return loopbacks

