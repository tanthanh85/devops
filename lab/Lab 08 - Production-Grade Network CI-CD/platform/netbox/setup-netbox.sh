#!/usr/bin/env bash
set -euo pipefail
target=${1:-$PWD/netbox-docker}
if [ -e "$target" ]; then echo "Target already exists: $target" >&2; exit 1; fi
git clone --branch release --single-branch https://github.com/netbox-community/netbox-docker.git "$target"
install -m 0644 "$(dirname "$0")/docker-compose.override.yml" "$target/docker-compose.override.yml"
install -m 0644 "$(dirname "$0")/filebeat.yml" "$target/filebeat.yml"
echo "Clone complete. Pin the instructor-approved release tag before starting NetBox."
