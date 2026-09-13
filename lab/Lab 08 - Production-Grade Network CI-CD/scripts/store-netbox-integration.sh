#!/usr/bin/env bash
set -euo pipefail
namespace=${KUBE_NAMESPACE:-network-devops}
: "${VAULT_BOOTSTRAP_TOKEN:?VAULT_BOOTSTRAP_TOKEN is required}"
: "${NETBOX_URL:?NETBOX_URL is required}"
: "${NETBOX_API_TOKEN:?NETBOX_API_TOKEN is required}"
payload=$(python3 -c 'import json,os; print(json.dumps({"data":{"url":os.environ["NETBOX_URL"],"token":os.environ["NETBOX_API_TOKEN"],"verify_tls":os.environ.get("NETBOX_VERIFY_TLS","true").lower()=="true"}}))')
kubectl -n "$namespace" port-forward service/vault 18200:8200 >/tmp/lab08-vault-forward.log 2>&1 & pid=$!
trap 'kill "$pid" 2>/dev/null || true' EXIT
for attempt in $(seq 1 30); do curl -fsS http://127.0.0.1:18200/v1/sys/health >/dev/null && break; sleep 1; done
curl -fsS -H "X-Vault-Token: $VAULT_BOOTSTRAP_TOKEN" -H 'Content-Type: application/json' --data "$payload" http://127.0.0.1:18200/v1/secret/data/integrations/netbox >/dev/null
echo "Stored the NetBox integration in Vault without printing its token."

