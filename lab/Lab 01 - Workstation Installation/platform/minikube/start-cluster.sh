#!/usr/bin/env bash
set -euo pipefail
minikube start --driver=docker --cpus=4 --memory=8192 --disk-size=30g --profile network-devops
minikube profile network-devops
kubectl get namespace network-devops >/dev/null 2>&1 || kubectl create namespace network-devops
kubectl get nodes -o wide
