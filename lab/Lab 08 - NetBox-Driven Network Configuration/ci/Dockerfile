FROM python:3.12-bookworm

ARG KUBECTL_VERSION=v1.31.4
ARG MINIKUBE_VERSION=v1.35.0

RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
       bash ca-certificates coreutils curl docker.io git jq openssh-client unzip \
    && architecture="$(dpkg --print-architecture)" \
    && case "$architecture" in amd64|arm64) ;; *) echo "Unsupported architecture: $architecture" >&2; exit 1 ;; esac \
    && curl -fsSLo /usr/local/bin/kubectl \
       "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${architecture}/kubectl" \
    && curl -fsSLo /usr/local/bin/minikube \
       "https://storage.googleapis.com/minikube/releases/${MINIKUBE_VERSION}/minikube-linux-${architecture}" \
    && chmod 0755 /usr/local/bin/kubectl /usr/local/bin/minikube \
    && mkdir -p /home/ubuntu/.kube /home/ubuntu/.minikube \
    && rm -rf /var/lib/apt/lists/*

ENV HOME=/home/ubuntu
WORKDIR /workspace
