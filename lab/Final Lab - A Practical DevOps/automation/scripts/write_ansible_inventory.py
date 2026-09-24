#!/usr/bin/env python3
import json
import os
import stat
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


if len(sys.argv) != 3:
    raise SystemExit("Usage: write_ansible_inventory.py <dev|production> <output.json>")

target, output_name = sys.argv[1:]
settings = {
    "dev": ("DEV_ROUTER_IP", "TF_VAR_dev_username", "TF_VAR_dev_password", "DEV_ROUTER_RESTCONF_PORT"),
    "production": ("PROD_ROUTER_HOST", None, None, "PROD_ROUTER_RESTCONF_PORT"),
}
if target not in settings:
    raise SystemExit(f"Unsupported inventory target: {target}")

host_key, username_key, password_key, port_key = settings[target]
required_keys = [host_key]
if target == "dev":
    required_keys.extend((username_key, password_key))
else:
    required_keys.extend(("VAULT_ADDR", "VAULT_TOKEN"))
values = {key: os.environ.get(key, "") for key in required_keys}
missing = [key for key, value in values.items() if not value]
if missing:
    raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")

for key in required_keys:
    if "\n" in values[key] or "\r" in values[key]:
        raise SystemExit(f"{key} must be a GitLab variable, not a multiline or file variable")
    if Path(values[key]).is_file():
        raise SystemExit(f"{key} appears to contain a file path; set its GitLab CI/CD variable Type to Variable")

if target == "production":
    vault_addr = values["VAULT_ADDR"].rstrip("/")
    parsed_vault_addr = urlparse(vault_addr)
    if parsed_vault_addr.scheme not in {"http", "https"} or not parsed_vault_addr.netloc:
        raise SystemExit("VAULT_ADDR must be a complete http:// or https:// URL")
    request = Request(
        f"{vault_addr}/v1/secret/data/lab8/production-router",
        headers={"X-Vault-Token": values["VAULT_TOKEN"], "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            vault_secret = json.load(response)["data"]["data"]
    except HTTPError as error:
        raise SystemExit(f"Vault rejected the production-router secret request with HTTP {error.code}") from None
    except (URLError, TimeoutError, OSError) as error:
        raise SystemExit(f"Unable to reach Vault at {vault_addr}: {error}") from None
    except (KeyError, TypeError, ValueError):
        raise SystemExit("Vault secret secret/lab8/production-router is missing username or password") from None
    username = str(vault_secret.get("username", ""))
    password = str(vault_secret.get("password", ""))
    if not username or not password:
        raise SystemExit("Vault secret secret/lab8/production-router is missing username or password")
else:
    username = values[username_key]
    password = values[password_key]

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
                        "ansible_user": username,
                        "ansible_password": password,
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
