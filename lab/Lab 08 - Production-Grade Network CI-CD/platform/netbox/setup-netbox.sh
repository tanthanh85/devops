#!/usr/bin/env bash
set -euo pipefail
target=${1:-$PWD/netbox-docker}
ref=${2:-}
if [ -z "$ref" ]; then
  echo "Usage: $0 <target-directory> <instructor-approved-release-tag>" >&2
  exit 2
fi
if [ -e "$target" ]; then echo "Target already exists: $target" >&2; exit 1; fi
git clone --branch "$ref" --single-branch --depth 1 https://github.com/netbox-community/netbox-docker.git "$target"
install -m 0644 "$(dirname "$0")/docker-compose.override.yml" "$target/docker-compose.override.yml"
install -m 0644 "$(dirname "$0")/filebeat.yml" "$target/filebeat.yml"
echo "NetBox Docker release $ref is ready in $target."
