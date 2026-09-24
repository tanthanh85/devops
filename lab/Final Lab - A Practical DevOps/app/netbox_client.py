from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlsplit

from flask import current_app
import requests


def _settings(base_url, token):
    base_url = str(base_url).strip().rstrip("/")
    token = str(token).strip()
    if not base_url or not token:
        raise RuntimeError("NetBox API is not configured")
    parsed = urlsplit(base_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("NetBox URL must be an HTTP(S) base URL without embedded credentials")

    return base_url, f"Bearer {token}" if token.startswith("nbt_") else f"Token {token}"


def _get(base_url, token, path, params):
    base_url, authorization = _settings(base_url, token)

    response = requests.get(
        f"{base_url}/api/{path}/",
        params=params,
        headers={"Authorization": authorization, "Accept": "application/json"},
        timeout=(5, 30),
        verify=current_app.config["NETBOX_VERIFY_TLS"],
    )
    response.raise_for_status()
    return response.json().get("results", [])


def fetch_devices(base_url, token):
    devices = []
    for item in _get(base_url, token, "dcim/devices", {"status": "active", "limit": 0}):
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


def fetch_loopbacks(device, base_url, token):
    loopbacks = []
    interfaces = _get(base_url, token, "dcim/interfaces", {"device": device, "type": "virtual", "limit": 0})
    for interface in interfaces:
        name = str(interface.get("name", ""))
        if not re.fullmatch(r"Loopback\d+", name, re.IGNORECASE):
            continue
        addresses = _get(base_url, token, "ipam/ip-addresses", {"interface_id": interface["id"], "limit": 0})
        for item in addresses:
            value = ipaddress.ip_interface(item["address"])
            if value.version == 4 and value.network.prefixlen == 32:
                loopbacks.append({"name": name, "ip": str(value.ip), "mask": "255.255.255.255"})
    return sorted(loopbacks, key=lambda item: item["name"])
