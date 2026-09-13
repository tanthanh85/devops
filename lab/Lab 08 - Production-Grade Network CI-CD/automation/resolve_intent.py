from hashlib import sha256
import json
import os
import re

from common import api_path, netbox_request


ip_id = os.environ["NETBOX_IP_ID"]
if not re.fullmatch(r"[1-9][0-9]*", ip_id):
    raise ValueError("NETBOX_IP_ID must be a positive integer")
address = netbox_request(f"/api/ipam/ip-addresses/{ip_id}/")
assigned = address.get("assigned_object") or {}
if not assigned.get("url"):
    raise ValueError("IP address must be assigned to a NetBox interface")
interface = netbox_request(api_path(assigned["url"]))
if not re.fullmatch(r"Loopback[0-9]{1,4}", str(interface.get("name", "")), re.I):
    raise ValueError("Only Loopback0 through Loopback9999 are allowed")
learner_id = str((interface.get("custom_fields") or {}).get("course_learner_id", "")).upper()
if not re.fullmatch(r"L(?:0[1-9]|1[0-9]|20)", learner_id):
    raise ValueError("NetBox interface must have course_learner_id L01 through L20")
expected_interface = f"Loopback{1000 + int(learner_id[1:])}"
if interface["name"].lower() != expected_interface.lower():
    raise ValueError(f"{learner_id} may manage only {expected_interface}")
device = netbox_request(api_path((interface.get("device") or {})["url"]))
intent = {
    "schema_version": 1,
    "netbox_ip_id": int(ip_id),
    "device": device["name"],
    "learner_id": learner_id,
    "interface": interface["name"],
    "address": address["address"],
}
canonical = json.dumps(intent, sort_keys=True, separators=(",", ":"))
intent["fingerprint"] = sha256(canonical.encode()).hexdigest()
with open("intent.json", "w", encoding="utf-8") as handle:
    json.dump(intent, handle, indent=2, sort_keys=True)
print(json.dumps({k: v for k, v in intent.items() if k != "address"} | {"address": intent["address"]}))
