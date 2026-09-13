from __future__ import annotations

from datetime import datetime, timezone
import ipaddress
import json
import os
import re
import time
from urllib.parse import urlparse

import hvac
import requests


def emit(action, outcome, started, **fields):
    event = {"@timestamp": datetime.now(timezone.utc).isoformat(), "message": action.replace("_", " "), "event.dataset": "network_cicd.audit", "event.category": "configuration", "event.type": "info", "event.action": action, "event.outcome": outcome, "event.duration_ms": round((time.perf_counter()-started)*1000, 2), "ci.pipeline.id": os.getenv("CI_PIPELINE_ID", "local"), "ci.job.id": os.getenv("CI_JOB_ID", "local"), **fields}
    try:
        from audit import send
        send(event)
    except ImportError:
        pass
    print(json.dumps(event, separators=(",", ":"), default=str), flush=True)


def vault_client():
    client = hvac.Client(url=os.getenv("VAULT_ADDR", "http://vault:8200"), timeout=5)
    method = os.getenv("VAULT_AUTH_METHOD", "kubernetes")
    if method == "approle":
        login = client.auth.approle.login(
            role_id=os.environ["VAULT_ROLE_ID"],
            secret_id=os.environ["VAULT_SECRET_ID"],
        )
    elif method == "jwt":
        login = client.auth.jwt.jwt_login(
            role=os.getenv("VAULT_JWT_ROLE", "gitlab-network-cicd"),
            jwt=os.environ["VAULT_ID_TOKEN"],
            path=os.getenv("VAULT_JWT_PATH", "jwt"),
        )
    else:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token", encoding="utf-8") as handle:
            jwt = handle.read().strip()
        login = client.auth.kubernetes.login(role="netbox-automation", jwt=jwt)
    client.token = login["auth"]["client_token"]
    return client


def vault_secret(path):
    return vault_client().secrets.kv.v2.read_secret_version(mount_point="secret", path=path)["data"]["data"]


def netbox_request(path):
    integration = vault_secret("integrations/netbox")
    response = requests.get(f"{str(integration['url']).rstrip('/')}{path}", headers={"Authorization": f"Token {integration['token']}", "Accept": "application/json"}, timeout=10, verify=integration.get("verify_tls", True))
    response.raise_for_status()
    return response.json()


def api_path(url):
    path = urlparse(url).path
    if not path.startswith("/api/"):
        raise ValueError("NetBox object URL is outside the API")
    return path


def desired_loopback():
    intent_file = os.getenv("INTENT_FILE", "intent.json")
    if os.path.exists(intent_file):
        with open(intent_file, encoding="utf-8") as handle:
            intent = json.load(handle)
    else:
        ip_id = os.environ["NETBOX_IP_ID"]
        if not re.fullmatch(r"[1-9][0-9]*", ip_id):
            raise ValueError("NETBOX_IP_ID must be a positive integer")
        address_record = netbox_request(f"/api/ipam/ip-addresses/{ip_id}/")
        assigned = address_record.get("assigned_object") or {}
        interface_url = assigned.get("url")
        if not interface_url:
            raise ValueError("NetBox IP address is not assigned to an interface")
        interface = netbox_request(api_path(interface_url))
        name = str(interface.get("name", ""))
        if not re.fullmatch(r"Loopback[0-9]{1,4}", name, re.IGNORECASE):
            raise ValueError("assigned interface must be named Loopback0 through Loopback9999")
        device = netbox_request(api_path((interface.get("device") or {})["url"]))
        device_name = str(device.get("name", ""))
        interface_ip = ipaddress.ip_interface(address_record["address"])
        intent = {
            "netbox_ip_id": int(ip_id),
            "device": device_name,
            "interface": name,
            "address": str(interface_ip),
            "learner_id": str((interface.get("custom_fields") or {}).get("course_learner_id", "")).upper(),
        }
    name = intent["interface"]
    device_name = intent["device"]
    interface_ip = ipaddress.ip_interface(intent["address"])
    learner_id = str(intent.get("learner_id", "")).upper()
    if not re.fullmatch(r"L(?:0[1-9]|1[0-9]|20)", learner_id):
        raise ValueError("intent learner_id must be L01 through L20")
    expected_interface = f"Loopback{1000 + int(learner_id[1:])}"
    if name.lower() != expected_interface.lower():
        raise ValueError(f"{learner_id} may manage only {expected_interface}")
    if interface_ip.version != 4:
        raise ValueError("this lab supports IPv4 loopback addresses")
    environment = os.getenv("TARGET_ENVIRONMENT", "production")
    if environment == "test":
        credentials = vault_secret(f"network/test/c8000v/{learner_id}")
        target_name = f"TEST-{learner_id}-C8000V-{os.getenv('CI_PIPELINE_ID', 'local')}"
        management_ip = credentials["management_ip"]
    elif environment == "production":
        credentials = vault_secret(f"network/routers/{device_name}")
        target_name = device_name
        management_ip = credentials.get("host") or credentials.get("management_ip")
    else:
        raise ValueError("TARGET_ENVIRONMENT must be test or production")
    if not management_ip:
        raise ValueError("target management IP is missing from Vault")
    return {
        "device": target_name,
        "production_device": device_name,
        "learner_id": learner_id,
        "management_ip": management_ip,
        "port": int(credentials.get("port", 22)),
        "interface": name,
        "address": str(interface_ip),
        "ip": str(interface_ip.ip),
        "prefix_length": interface_ip.network.prefixlen,
        "netmask": str(interface_ip.network.netmask),
        "username": credentials["username"],
        "password": credentials["password"],
        "enabled": credentials.get("enabled", True),
        "ssh_host_key": credentials.get("ssh_host_key"),
        "environment": environment,
    }
