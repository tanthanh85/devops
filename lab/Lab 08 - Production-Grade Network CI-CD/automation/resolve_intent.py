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
device = netbox_request(api_path((interface.get("device") or {})["url"]))
intent = {
    "schema_version": 1,
    "netbox_ip_id": int(ip_id),
    "device": device["name"],
    "interface": interface["name"],
    "address": address["address"],
}
canonical = json.dumps(intent, sort_keys=True, separators=(",", ":"))
intent["fingerprint"] = sha256(canonical.encode()).hexdigest()
with open("intent.json", "w", encoding="utf-8") as handle:
    json.dump(intent, handle, indent=2, sort_keys=True)
print(json.dumps({k: v for k, v in intent.items() if k != "address"} | {"address": intent["address"]}))
