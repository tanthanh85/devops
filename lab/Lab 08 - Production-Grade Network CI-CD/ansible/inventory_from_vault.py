#!/usr/bin/env python3
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation"))

from common import desired_loopback


def main():
    desired = desired_loopback()
    host = desired["device"]
    known_hosts = Path(os.getenv("CI_PROJECT_DIR", "/workspace")) / "evidence/known_hosts"
    known_hosts.parent.mkdir(exist_ok=True)
    if desired.get("ssh_host_key"):
        known_hosts.write_text(f"{desired['management_ip']} {desired['ssh_host_key']}\n", encoding="utf-8")
    inventory = {
        "target": {"hosts": [host]},
        "_meta": {
            "hostvars": {
                host: {
                    "ansible_host": desired["management_ip"],
                    "ansible_port": desired.get("port", 22),
                    "ansible_user": desired["username"],
                    "ansible_password": desired["password"],
                    "ansible_ssh_common_args": f"-o UserKnownHostsFile={known_hosts} -o StrictHostKeyChecking=yes",
                    "ansible_connection": "ansible.netcommon.network_cli",
                    "ansible_network_os": "cisco.ios.ios",
                    "automation_enabled": desired.get("enabled", True),
                    "target_environment": desired["environment"],
                    "loopback_name": desired["interface"],
                    "loopback_address": desired["address"],
                    "loopback_ip": desired["ip"],
                    "loopback_netmask": desired["netmask"],
                }
            }
        },
    }
    print(json.dumps(inventory))


if __name__ == "__main__":
    main()
