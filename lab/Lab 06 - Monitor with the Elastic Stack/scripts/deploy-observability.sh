#!/usr/bin/env bash
set -euo pipefail

namespace=${KUBE_NAMESPACE:-network-devops}
: "${LOGSTASH_HOST:?Set LOGSTASH_HOST to the host and port reachable from Minikube}"

kubectl -n "$namespace" create configmap observability-endpoints \
  --from-literal=LOGSTASH_HOST="$LOGSTASH_HOST" \
  --dry-run=client -o yaml | kubectl apply -f - >/dev/null
kubectl apply -f kubernetes/filebeat.yaml
kubectl apply -f kubernetes/metricbeat.yaml
kubectl apply -f kubernetes/synthetic-monitor.yaml
kubectl -n "$namespace" rollout status daemonset/filebeat --timeout=180s
kubectl -n "$namespace" rollout status daemonset/metricbeat --timeout=180s
kubectl -n "$namespace" rollout status deployment/kube-state-metrics --timeout=180s
kubectl -n "$namespace" rollout status deployment/metricbeat-state --timeout=180s
kubectl -n "$namespace" rollout status deployment/network-monitor-synthetic --timeout=180s
