#!/usr/bin/env bash
set -euo pipefail

namespace=${KUBE_NAMESPACE:-network-devops-lab05}
: "${LOGSTASH_HOST:?Set LOGSTASH_HOST to the host and port reachable from Minikube}"
: "${E2E_USERNAME:?E2E_USERNAME is required}"
: "${E2E_PASSWORD:?E2E_PASSWORD is required}"

kubectl -n "$namespace" create configmap observability-endpoints \
  --from-literal=LOGSTASH_HOST="$LOGSTASH_HOST" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl -n "$namespace" create secret generic synthetic-monitor-credentials \
  --from-literal=username="$E2E_USERNAME" \
  --from-literal=password="$E2E_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f kubernetes/filebeat.yaml
kubectl apply -f kubernetes/metricbeat.yaml
kubectl apply -f kubernetes/synthetic-monitor.yaml
kubectl -n "$namespace" rollout status daemonset/filebeat --timeout=180s
kubectl -n "$namespace" rollout status daemonset/metricbeat --timeout=180s
kubectl -n "$namespace" rollout status deployment/kube-state-metrics --timeout=180s
kubectl -n "$namespace" rollout status deployment/metricbeat-state --timeout=180s

