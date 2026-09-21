import hmac
import ipaddress
import os
import re

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)


def nested(value, *keys):
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


@app.get("/health")
def health():
    return jsonify(status="ready", tier="config")


@app.post("/webhooks/netbox")
def netbox_webhook():
    expected = os.environ.get("NETBOX_WEBHOOK_TOKEN", "")
    supplied = request.headers.get("X-NetBox-Webhook-Token", "")
    if not expected or not hmac.compare_digest(supplied, expected):
        return jsonify(error="invalid webhook token"), 401

    payload = request.get_json(silent=True) or {}
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    event = str(payload.get("event", data.get("event", ""))).lower()
    object_type = str(payload.get("object_type", payload.get("model", data.get("object_type", "")))).lower()
    address = str(data.get("address", "")).strip()
    assigned = data.get("assigned_object") or {}
    interface_name = str(assigned.get("name", data.get("interface_name", ""))).strip()
    device_name = str(nested(assigned, "device", "name") or data.get("device_name", "")).strip()
    expected_device = os.environ.get("NETBOX_ROUTER_NAME", "").strip()
    if not expected_device:
        return jsonify(error="learner router name is not configured"), 503

    try:
        network = ipaddress.ip_interface(address)
    except ValueError:
        return jsonify(status="ignored", reason="invalid or missing address"), 202

    is_ip_event = object_type in {"ipaddress", "ipam.ipaddress", "ipam.ipaddresses"}
    if event not in {"created", "updated"} or not is_ip_event:
        return jsonify(status="ignored", reason="not an IP address create/update event"), 202
    if network.version != 4 or network.network.prefixlen != 32:
        return jsonify(status="ignored", reason="address is not IPv4 /32"), 202
    if device_name != expected_device:
        return jsonify(status="ignored", reason="event is not for the lab router"), 202
    if not re.fullmatch(r"Loopback\d+", interface_name, re.IGNORECASE):
        return jsonify(status="ignored", reason="assigned interface is not a loopback"), 202

    project_id = os.environ["GITLAB_PROJECT_ID"]
    trigger_url = f"{os.environ.get('GITLAB_URL', 'https://gitlab.com').rstrip('/')}/api/v4/projects/{project_id}/trigger/pipeline"
    response = requests.post(
        trigger_url,
        data={
            "token": os.environ["GITLAB_TRIGGER_TOKEN"],
            "ref": os.environ.get("GITLAB_REF", "main"),
            "variables[NETBOX_ACTION]": "provision_loopback",
            "variables[NETBOX_DEVICE]": device_name,
            "variables[LOOPBACK_NAME]": interface_name,
            "variables[LOOPBACK_ADDRESS]": address,
        },
        timeout=20,
    )
    response.raise_for_status()
    pipeline = response.json()
    app.logger.info("NetBox event accepted; GitLab pipeline %s created", pipeline.get("id"))
    return jsonify(status="triggered", pipeline_id=pipeline.get("id"), interface=interface_name, address=address), 202
