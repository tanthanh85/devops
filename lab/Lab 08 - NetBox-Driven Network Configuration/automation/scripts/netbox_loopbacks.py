#!/usr/bin/env python3
import ipaddress
import json
import os
import re
import ssl
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def get(path, params):
    base = os.environ["NETBOX_URL"].rstrip("/")
    request = Request(
        f"{base}/api/{path}/?{urlencode(params)}",
        headers={"Authorization": f"Token {os.environ['NETBOX_API_TOKEN']}", "Accept": "application/json"},
    )
    context = ssl._create_unverified_context() if os.environ.get("NETBOX_SKIP_TLS_VERIFY", "false").lower() == "true" else None
    with urlopen(request, timeout=30, context=context) as response:
        return json.load(response).get("results", [])


device = os.environ["NETBOX_DEVICE"]
interfaces = get("dcim/interfaces", {"device": device, "type": "virtual", "limit": 0})
loopbacks = []
for interface in interfaces:
    name = interface.get("name", "")
    if not re.fullmatch(r"Loopback\d+", name, re.IGNORECASE):
        continue
    addresses = get("ipam/ip-addresses", {"interface_id": interface["id"], "limit": 0})
    for address_object in addresses:
        interface_address = ipaddress.ip_interface(address_object["address"])
        if interface_address.version == 4 and interface_address.network.prefixlen == 32:
            loopbacks.append({"name": name, "ip": str(interface_address.ip), "mask": "255.255.255.255"})

loopbacks.sort(key=lambda item: item["name"])
if not loopbacks:
    raise SystemExit(f"No IPv4 /32 loopback addresses found in NetBox for {device}")

output = Path("build/netbox-loopbacks.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps({"netbox_device": device, "netbox_loopback_count": len(loopbacks), "netbox_loopbacks": loopbacks}, indent=2) + "\n")
print(f"Wrote {len(loopbacks)} NetBox loopbacks for {device} to {output}")
