#!/usr/bin/env bash
set -euo pipefail

namespace=${KUBE_NAMESPACE:-network-devops}
: "${VAULT_BOOTSTRAP_TOKEN:?VAULT_BOOTSTRAP_TOKEN is required}"

vault_exec() {
  kubectl -n "$namespace" exec deployment/vault -- env \
    VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" vault "$@"
}

vault_exec secrets enable -path=secret kv-v2 2>/dev/null || true
vault_exec auth enable kubernetes 2>/dev/null || true

kubernetes_host=https://kubernetes.default.svc:443

vault_exec write auth/kubernetes/config \
  kubernetes_host="$kubernetes_host" >/dev/null

policy='path "secret/data/network/routers/*" { capabilities = ["read"] }
path "secret/metadata/network/routers" { capabilities = ["list"] }'
printf '%s\n' "$policy" | kubectl -n "$namespace" exec -i deployment/vault -- env \
  VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" \
  vault policy write network-monitor - >/dev/null

vault_exec write auth/kubernetes/role/network-monitor \
  bound_service_account_names=network-monitor-app \
  bound_service_account_namespaces="$namespace" \
  policies=network-monitor ttl=15m >/dev/null

echo "Vault Kubernetes authentication and least-privilege policy are configured."
