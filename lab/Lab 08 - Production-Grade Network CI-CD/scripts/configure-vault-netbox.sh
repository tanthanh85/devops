#!/usr/bin/env bash
set -euo pipefail
namespace=${KUBE_NAMESPACE:-network-devops}
: "${VAULT_BOOTSTRAP_TOKEN:?VAULT_BOOTSTRAP_TOKEN is required}"
vault_exec() { kubectl -n "$namespace" exec deployment/vault -- env VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" vault "$@"; }

app_policy='path "secret/metadata/network/routers" { capabilities = ["list"] }
path "secret/data/network/routers/*" { capabilities = ["read"] }
path "secret/data/integrations/netbox" { capabilities = ["read"] }'
printf '%s\n' "$app_policy" | kubectl -n "$namespace" exec -i deployment/vault -- env VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" vault policy write network-monitor - >/dev/null

automation_policy='path "secret/data/network/routers/*" { capabilities = ["read"] }
path "secret/data/network/test/c8000v" { capabilities = ["read"] }
path "secret/data/integrations/netbox" { capabilities = ["read"] }
path "secret/data/integrations/cml" { capabilities = ["read"] }
path "secret/data/integrations/elastic-audit" { capabilities = ["read"] }'
printf '%s\n' "$automation_policy" | kubectl -n "$namespace" exec -i deployment/vault -- env VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" vault policy write netbox-automation - >/dev/null
vault_exec write auth/kubernetes/role/netbox-automation bound_service_account_names=netbox-automation bound_service_account_namespaces="$namespace" policies=netbox-automation ttl=15m >/dev/null
vault_exec auth enable approle >/dev/null 2>&1 || true
vault_exec write auth/approle/role/gitlab-network-cicd token_policies=netbox-automation token_ttl=15m token_max_ttl=30m secret_id_ttl=24h secret_id_num_uses=20 >/dev/null
echo "Configured application, Kubernetes automation, and short-lived GitLab AppRole access policies."
echo "An instructor may retrieve a role ID and issue a limited SecretID for protected, masked GitLab variables."
