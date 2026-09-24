#!/usr/bin/env python3
import json
import os
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

base = os.environ["NETWORK_MONITOR_URL"].rstrip("/")
device = os.environ["NETBOX_ROUTER_NAME"]
request = Request(
    f"{base}/api/internal/netbox/loopbacks?{urlencode({'device': device})}",
    headers={"X-Internal-Token": os.environ["FLASK_SECRET_KEY"], "Accept": "application/json"},
)
with urlopen(request, timeout=30) as response:
    payload = json.load(response)

if not payload.get("netbox_loopbacks"):
    raise SystemExit(f"No IPv4 /32 loopback addresses found in NetBox for {device}")

output = Path("build/netbox-loopbacks.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(payload, indent=2) + "\n")
print(f"Wrote {payload['netbox_loopback_count']} NetBox loopbacks for {device} to {output}")
