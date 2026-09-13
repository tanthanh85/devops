#!/usr/bin/env bash
set -euo pipefail
kubectl apply -f kubernetes/namespace.yaml
kubectl apply -f kubernetes/configmap.yaml
bash scripts/create-secrets.sh
kubectl apply -f kubernetes/token-review.yaml
kubectl apply -f kubernetes/vault.yaml
kubectl -n network-devops rollout status deployment/vault --timeout=180s
bash scripts/configure-vault.sh
kubectl apply -f kubernetes/mysql.yaml
kubectl -n network-devops rollout status deployment/mysql --timeout=180s
kubectl apply -f kubernetes/app.yaml
kubectl -n network-devops rollout status deployment/network-monitor-app --timeout=180s
kubectl apply -f kubernetes/web.yaml
kubectl -n network-devops rollout status deployment/network-monitor-web --timeout=180s
kubectl -n network-devops get pod,service,pvc -o wide
