from __future__ import annotations

import ipaddress

from flask import current_app
import requests


def fetch_devices():
    base_url = current_app.config["NETBOX_URL"].rstrip("/")
    token = current_app.config["NETBOX_API_TOKEN"]
    if not base_url or not token:
        raise RuntimeError("NetBox API is not configured")

    response = requests.get(
        f"{base_url}/api/dcim/devices/",
        params={"status": "active", "limit": 0},
        headers={"Authorization": f"Token {token}", "Accept": "application/json"},
        timeout=(5, 30),
        verify=current_app.config["NETBOX_VERIFY_TLS"],
    )
    response.raise_for_status()
    devices = []
    for item in response.json().get("results", []):
        primary = item.get("primary_ip4") or item.get("primary_ip") or {}
        address = primary.get("address") if isinstance(primary, dict) else ""
        if not address:
            continue
        management_ip = str(ipaddress.ip_interface(address).ip)
        custom_fields = item.get("custom_fields") or {}
        port = int(custom_fields.get("restconf_port") or 443)
        if not 1 <= port <= 65535:
            raise ValueError(f"invalid RESTCONF port for {item.get('name', 'unnamed device')}")
        devices.append({
            "name": str(item["name"]),
            "host": management_ip,
            "port": port,
        })
    return devices
