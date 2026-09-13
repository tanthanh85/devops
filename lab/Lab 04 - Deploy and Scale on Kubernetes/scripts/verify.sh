#!/usr/bin/env bash
set -euo pipefail
namespace=network-devops
kubectl -n "$namespace" wait --for=condition=available deployment/mysql --timeout=180s
kubectl -n "$namespace" wait --for=condition=available deployment/vault --timeout=180s
kubectl -n "$namespace" wait --for=condition=available deployment/network-monitor-app --timeout=180s
kubectl -n "$namespace" wait --for=condition=available deployment/network-monitor-web --timeout=180s
ready=$(kubectl -n "$namespace" get pods -l app=network-monitor,tier=web --field-selector=status.phase=Running --no-headers | awk '$2 ~ /^1\/1$/ {count++} END {print count+0}')
expected=$(kubectl -n "$namespace" get deployment network-monitor-web -o jsonpath='{.spec.replicas}')
test "$ready" -eq "$expected"
kubectl -n "$namespace" get endpointslice -l kubernetes.io/service-name=network-monitor-web
echo "Verified $ready ready web Pods."
