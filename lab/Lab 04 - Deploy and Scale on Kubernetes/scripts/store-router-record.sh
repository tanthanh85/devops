#!/usr/bin/env bash
set -euo pipefail

namespace=${KUBE_NAMESPACE:-network-devops}
: "${VAULT_BOOTSTRAP_TOKEN:?VAULT_BOOTSTRAP_TOKEN is required}"
: "${ROUTER_NAME:?ROUTER_NAME is required}"
: "${ROUTER_HOST:?ROUTER_HOST is required}"
: "${ROUTER_USERNAME:?ROUTER_USERNAME is required}"
: "${ROUTER_PASSWORD:?ROUTER_PASSWORD is required}"
ROUTER_PORT=${ROUTER_PORT:-443}

if [[ ! "$ROUTER_NAME" =~ ^[A-Za-z0-9_.-]{1,80}$ ]]; then
  echo "ROUTER_NAME is not a safe Vault path component." >&2
  exit 1
fi

payload=$(python3 -c 'import json,os; print(json.dumps({"data":{"host":os.environ["ROUTER_HOST"],"port":int(os.environ["ROUTER_PORT"]),"username":os.environ["ROUTER_USERNAME"],"password":os.environ["ROUTER_PASSWORD"],"enabled":True}}))')
kubectl -n "$namespace" port-forward service/vault 18200:8200 >/tmp/lab04-vault-forward.log 2>&1 &
forward_pid=$!
trap 'kill "$forward_pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 30); do
  curl --fail --silent http://127.0.0.1:18200/v1/sys/health >/dev/null && break
  sleep 1
done
curl --fail --silent --show-error \
  --header "X-Vault-Token: $VAULT_BOOTSTRAP_TOKEN" \
  --header "Content-Type: application/json" \
  --request POST --data "$payload" \
  "http://127.0.0.1:18200/v1/secret/data/network/routers/$ROUTER_NAME" >/dev/null
echo "Stored the router record at secret/data/network/routers/$ROUTER_NAME without printing it."
