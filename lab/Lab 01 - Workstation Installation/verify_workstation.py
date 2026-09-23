from __future__ import annotations

import json
import shutil
import subprocess
import sys


COMMANDS = {
    "Python": [sys.executable, "--version"],
    "pip": [sys.executable, "-m", "pip", "--version"],
    "Git": ["git", "--version"],
    "Ansible": ["ansible", "--version"],
    "Ansible Playbook": ["ansible-playbook", "--version"],
    "Ansible Galaxy": ["ansible-galaxy", "--version"],
    "Terraform": ["terraform", "version"],
    "Docker": ["docker", "--version"],
    "Docker Compose": ["docker", "compose", "version"],
    "kubectl": ["kubectl", "version", "--client", "-o", "json"],
    "Minikube": ["minikube", "version", "--output=json"],
}


def check(name: str, command: list[str]) -> bool:
    if shutil.which(command[0]) is None:
        print(f"FAIL {name}: executable not found")
        return False
    result = subprocess.run(command, text=True, capture_output=True, timeout=20)
    output = (result.stdout or result.stderr).splitlines()
    summary = output[0][:120] if output else "no output"
    print(f"{'PASS' if result.returncode == 0 else 'FAIL'} {name}: {summary}")
    return result.returncode == 0


def main() -> int:
    results = {name: check(name, command) for name, command in COMMANDS.items()}
    print(json.dumps(results, indent=2))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
