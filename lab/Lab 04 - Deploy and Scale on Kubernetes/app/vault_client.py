from __future__ import annotations

from dataclasses import dataclass
import re

import hvac
from flask import current_app


@dataclass(frozen=True)
class RouterRecord:
    name: str
    host: str
    port: int
    username: str
    password: str
    ca_bundle_name: str | None
    enabled: bool


def _safe_secret_name(router_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_.-]{1,80}", router_name):
        raise ValueError("router name cannot be mapped safely to Vault")
    return router_name


def _client():
    client = hvac.Client(
        url=current_app.config["VAULT_ADDR"],
        verify=current_app.config["VAULT_CACERT"] or True,
        timeout=5,
    )
    with open(current_app.config["KUBERNETES_TOKEN_PATH"], encoding="utf-8") as token_file:
        jwt = token_file.read().strip()
    login = client.auth.kubernetes.login(
        role=current_app.config["VAULT_KUBERNETES_ROLE"], jwt=jwt
    )
    client.token = login["auth"]["client_token"]
    return client


def read_router(router_name: str) -> RouterRecord:
    response = _client().secrets.kv.v2.read_secret_version(
        mount_point=current_app.config["VAULT_KV_MOUNT"],
        path=f"network/routers/{_safe_secret_name(router_name)}",
        raise_on_deleted_version=True,
    )
    values = response["data"]["data"]
    if any(not str(values.get(field, "")).strip() for field in ("host", "username", "password")):
        raise ValueError("Vault router record is missing a required field")
    port = int(values.get("port", 443))
    if not 1 <= port <= 65535:
        raise ValueError("Vault router record contains an invalid port")
    return RouterRecord(router_name, str(values["host"]).strip(), port,
                        str(values["username"]), str(values["password"]),
                        str(values.get("ca_bundle_name") or "") or None,
                        bool(values.get("enabled", True)))


def list_routers() -> list[dict]:
    response = _client().secrets.kv.v2.list_secrets(
        mount_point=current_app.config["VAULT_KV_MOUNT"], path="network/routers"
    )
    items = []
    for name in sorted(response.get("data", {}).get("keys", [])):
        if name.endswith("/"):
            continue
        router = read_router(name)
        items.append({"name": router.name, "host": router.host, "port": router.port,
                      "ca_bundle_name": router.ca_bundle_name, "enabled": router.enabled,
                      "credential_source": "vault"})
    return items
