#!/usr/bin/env bash
set -euo pipefail

namespace=${KUBE_NAMESPACE:-network-devops}
: "${E2E_USERNAME:?E2E_USERNAME is required}"
: "${E2E_PASSWORD:?E2E_PASSWORD is required}"

if [[ ! "$E2E_USERNAME" =~ ^[a-z][a-z0-9_.-]{2,31}$ ]]; then
  echo "E2E_USERNAME must match the application username policy." >&2
  exit 1
fi

if [ "${#E2E_PASSWORD}" -lt 12 ]; then
  echo "E2E_PASSWORD must contain at least 12 characters." >&2
  exit 1
fi

kubectl -n "$namespace" create secret generic e2e-test-credentials \
  --from-literal=username="$E2E_USERNAME" \
  --from-literal=password="$E2E_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null

cleanup() {
  kubectl -n "$namespace" delete secret e2e-test-credentials \
    --ignore-not-found >/dev/null
}
trap cleanup EXIT

kubectl -n "$namespace" delete job provision-e2e-user \
  --ignore-not-found --wait=true >/dev/null
kubectl apply -f kubernetes/test-user-job.yaml >/dev/null
kubectl -n "$namespace" wait --for=condition=complete job/provision-e2e-user \
  --timeout=120s
kubectl -n "$namespace" logs job/provision-e2e-user
