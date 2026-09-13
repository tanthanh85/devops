#!/usr/bin/env bash
set -euo pipefail
namespace=${KUBE_NAMESPACE:-network-devops}
: "${VAULT_BOOTSTRAP_TOKEN:?VAULT_BOOTSTRAP_TOKEN is required}"
: "${CML_ADDRESS:?CML_ADDRESS is required and must use https://}"
: "${CML_TOKEN:?CML_TOKEN is required}"
: "${LEARNER_ID:?LEARNER_ID is required (L01-L20)}"
[[ "$LEARNER_ID" =~ ^L(0[1-9]|1[0-9]|20)$ ]] || { echo "LEARNER_ID must be L01 through L20" >&2; exit 2; }
: "${TEST_ROUTER_IP:?TEST_ROUTER_IP is required}"
: "${TEST_ROUTER_PREFIX_LENGTH:?TEST_ROUTER_PREFIX_LENGTH is required}"
: "${TEST_ROUTER_GATEWAY:?TEST_ROUTER_GATEWAY is required}"
: "${TEST_ROUTER_USERNAME:?TEST_ROUTER_USERNAME is required}"
: "${TEST_ROUTER_PASSWORD:?TEST_ROUTER_PASSWORD is required}"
: "${ELASTIC_AUDIT_URL:?ELASTIC_AUDIT_URL is required}"
: "${ELASTIC_AUDIT_API_KEY:?ELASTIC_AUDIT_API_KEY is required}"

vault_cmd=(kubectl -n "$namespace" exec deployment/vault -- env VAULT_ADDR=http://127.0.0.1:8200 VAULT_TOKEN="$VAULT_BOOTSTRAP_TOKEN" vault)
"${vault_cmd[@]}" kv put secret/integrations/cml address="$CML_ADDRESS" token="$CML_TOKEN" skip_verify="${CML_SKIP_VERIFY:-false}" external_connector="${CML_EXTERNAL_CONNECTOR:-bridge0}" node_definition="${CML_NODE_DEFINITION:-cat8000v}" image_definition="${CML_IMAGE_DEFINITION:-}" router_ram_mb="${CML_ROUTER_RAM_MB:-4096}" >/dev/null
"${vault_cmd[@]}" kv put "secret/network/test/c8000v/$LEARNER_ID" management_ip="$TEST_ROUTER_IP" prefix_length="$TEST_ROUTER_PREFIX_LENGTH" gateway="$TEST_ROUTER_GATEWAY" username="$TEST_ROUTER_USERNAME" password="$TEST_ROUTER_PASSWORD" port=22 enabled=true owner="$LEARNER_ID" >/dev/null
"${vault_cmd[@]}" kv put secret/integrations/elastic-audit url="$ELASTIC_AUDIT_URL" api_key="$ELASTIC_AUDIT_API_KEY" verify_tls="${ELASTIC_AUDIT_VERIFY_TLS:-true}" >/dev/null
echo "Stored CML, $LEARNER_ID ephemeral test-router, and Elastic audit integration records in Vault."
