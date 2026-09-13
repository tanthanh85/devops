#!/usr/bin/env python3
from datetime import datetime, timezone
import argparse
import json
import os
import ssl
import sys
import urllib.request
import uuid


SAFE_ENV = {
    "CI_PROJECT_ID": "gitlab.project.id",
    "CI_PROJECT_PATH": "gitlab.project.path",
    "CI_PIPELINE_ID": "ci.pipeline.id",
    "CI_PIPELINE_IID": "ci.pipeline.iid",
    "CI_PIPELINE_SOURCE": "ci.pipeline.source",
    "CI_JOB_ID": "ci.job.id",
    "CI_JOB_NAME": "ci.job.name",
    "CI_JOB_STAGE": "ci.job.stage",
    "CI_COMMIT_SHA": "git.commit.id",
    "CI_COMMIT_REF_NAME": "git.ref",
    "GITLAB_USER_ID": "user.id",
    "GITLAB_USER_LOGIN": "user.name",
    "CI_RUNNER_ID": "runner.id",
    "NETBOX_IP_ID": "netbox.ip_address.id",
    "TARGET_ENVIRONMENT": "deployment.environment",
}


def base_event():
    event = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
        "event.id": str(uuid.uuid4()),
        "event.schema_version": "1.0",
        "event.dataset": "network_cicd.audit",
        "service.name": "gitlab-network-delivery",
    }
    for source, destination in SAFE_ENV.items():
        if os.getenv(source):
            event[destination] = os.environ[source]
    return event


def send(event):
    url = os.environ.get("ELASTIC_AUDIT_URL")
    api_key = os.environ.get("ELASTIC_AUDIT_API_KEY")
    verify_tls = os.getenv("ELASTIC_AUDIT_VERIFY_TLS", "true")
    if not url:
        vault_addr = os.environ["VAULT_ADDR"].rstrip("/")
        login_body = json.dumps({
            "role_id": os.environ["VAULT_ROLE_ID"],
            "secret_id": os.environ["VAULT_SECRET_ID"],
        }).encode()
        login_request = urllib.request.Request(
            vault_addr + "/v1/auth/approle/login",
            data=login_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(login_request, timeout=10) as response:
            client_token = json.load(response)["auth"]["client_token"]
        secret_request = urllib.request.Request(
            vault_addr + "/v1/secret/data/integrations/elastic-audit",
            headers={"X-Vault-Token": client_token},
        )
        with urllib.request.urlopen(secret_request, timeout=10) as response:
            integration = json.load(response)["data"]["data"]
        url = integration["url"]
        api_key = integration.get("api_key")
        verify_tls = str(integration.get("verify_tls", True)).lower()
    if not url:
        raise RuntimeError("ELASTIC_AUDIT_URL is required; audit delivery fails closed")
    body = json.dumps(event, separators=(",", ":")).encode()
    headers = {"Content-Type": "application/json", "User-Agent": "network-cicd-audit/1.0"}
    if api_key:
        headers["Authorization"] = "ApiKey " + api_key
    context = ssl.create_default_context()
    if verify_tls != "true":
        context = ssl._create_unverified_context()
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(request, timeout=10, context=context) as response:
        if response.status >= 300:
            raise RuntimeError(f"audit endpoint returned HTTP {response.status}")


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    emit = sub.add_parser("emit")
    emit.add_argument("--action", required=True)
    emit.add_argument("--outcome", choices=["success", "failure", "unknown"], required=True)
    emit.add_argument("--category", default="configuration")
    emit.add_argument("--type", default="info")
    emit.add_argument("--message", required=True)
    emit.add_argument("--duration-ms", type=float)
    emit.add_argument("--fields-json", default="{}")
    args = parser.parse_args()
    event = base_event()
    event.update({
        "event.action": args.action,
        "event.outcome": args.outcome,
        "event.category": args.category,
        "event.type": args.type,
        "message": args.message[:500],
    })
    if args.duration_ms is not None:
        event["event.duration_ms"] = args.duration_ms
    fields = json.loads(args.fields_json)
    blocked = {"password", "token", "secret", "authorization", "credential"}
    if any(any(word in key.lower() for word in blocked) for key in fields):
        raise ValueError("audit field name may expose secret material")
    event.update(fields)
    send(event)
    print(json.dumps(event, separators=(",", ":")))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"audit delivery failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        raise
