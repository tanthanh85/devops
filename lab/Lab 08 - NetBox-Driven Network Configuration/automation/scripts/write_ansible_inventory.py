#!/usr/bin/env python3
import json
import os
import stat
import sys
from pathlib import Path


if len(sys.argv) != 3:
    raise SystemExit("Usage: write_ansible_inventory.py <dev|production> <output.json>")

target, output_name = sys.argv[1:]
settings = {
    "dev": ("DEV_ROUTER_IP", "TF_VAR_dev_username", "TF_VAR_dev_password", "DEV_ROUTER_RESTCONF_PORT"),
    "production": ("PROD_ROUTER_HOST", "PROD_ROUTER_USERNAME", "PROD_ROUTER_PASSWORD", "PROD_ROUTER_RESTCONF_PORT"),
}
if target not in settings:
    raise SystemExit(f"Unsupported inventory target: {target}")

host_key, username_key, password_key, port_key = settings[target]
values = {key: os.environ.get(key, "") for key in (host_key, username_key, password_key)}
missing = [key for key, value in values.items() if not value]
if missing:
    raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

for key in (username_key, password_key):
    if "\n" in values[key] or "\r" in values[key]:
        raise SystemExit(f"{key} must be a GitLab variable, not a multiline or file variable")
    if Path(values[key]).is_file():
        raise SystemExit(f"{key} appears to contain a file path; set its GitLab CI/CD variable Type to Variable")

try:
    port = int(os.environ.get(port_key, "443"))
except ValueError as exc:
    raise SystemExit(f"{port_key} must be an integer from 1 through 65535") from exc
if not 1 <= port <= 65535:
    raise SystemExit(f"{port_key} must be an integer from 1 through 65535")

inventory = {
    "all": {
        "children": {
            "routers": {
                "hosts": {
                    target: {
                        "ansible_host": values[host_key],
                        "ansible_user": values[username_key],
                        "ansible_password": values[password_key],
                        "ansible_connection": "ansible.netcommon.httpapi",
                        "ansible_network_os": "ansible.netcommon.restconf",
                        "ansible_httpapi_use_ssl": True,
                        "ansible_httpapi_validate_certs": False,
                        "ansible_port": port,
                    }
                }
            }
        }
    }
}

output = Path(output_name)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(inventory) + "\n")
output.chmod(stat.S_IRUSR | stat.S_IWUSR)
print(f"Wrote protected Ansible inventory for {target} at {output}")
