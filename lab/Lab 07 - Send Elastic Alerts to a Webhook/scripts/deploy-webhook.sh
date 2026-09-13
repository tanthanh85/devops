#!/usr/bin/env bash
set -euo pipefail

namespace=${KUBE_NAMESPACE:-network-devops}
: "${WEBHOOK_TOKEN:?WEBHOOK_TOKEN is required}"
if [ "${#WEBHOOK_TOKEN}" -lt 24 ]; then
  echo "WEBHOOK_TOKEN must contain at least 24 characters." >&2
  exit 1
fi
kubectl -n "$namespace" create secret generic alert-webhook-token \
  --from-literal=token="$WEBHOOK_TOKEN" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f kubernetes/webhook-receiver.yaml
kubectl -n "$namespace" rollout status deployment/alert-webhook --timeout=120s
kubectl -n "$namespace" get service alert-webhook -o wide

