from __future__ import annotations

import time

from flask import current_app
import requests

CPU_PATH = "/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization"
MEMORY_PATH = "/restconf/data/Cisco-IOS-XE-memory-oper:memory-statistics/memory-statistic"


def _find(value, names):
    if isinstance(value, dict):
        for key, child in value.items():
            if key.split(":")[-1] in names and isinstance(child, (int, float, str)):
                try:
                    return float(child)
                except ValueError:
                    pass
            found = _find(child, names)
            if found is not None:
                return found
    if isinstance(value, list):
        for child in value:
            found = _find(child, names)
            if found is not None:
                return found
    return None


def _restconf_get(router, path, metric, request_options):
    url = f"https://{router.host}:{router.port}{path}"
    request_payload = {
        "method": "GET",
        "url": url,
        "headers": {"Accept": request_options["headers"]["Accept"]},
        "body": None,
    }
    fields = {
        "event.action": "restconf_request",
        "network.protocol": "restconf",
        "http.request.method": "GET",
        "url.path": path,
        "network.router.name": router.name,
        "network.router.address": router.host,
        "network.router.metric": metric,
        "restconf.request.payload": request_payload,
    }
    current_app.logger.info("RESTCONF GET %s", path, extra={"event_fields": fields})

    started = time.perf_counter()
    try:
        response = requests.get(
            url,
            **request_options,
        )
    except requests.RequestException as exc:
        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        current_app.logger.warning(
            "RESTCONF failed %s %.2fms",
            type(exc).__name__,
            duration_ms,
            extra={"event_fields": {
                **fields,
                "event.action": "restconf_response",
                "event.outcome": "failure",
                "event.duration_ms": duration_ms,
                "error.type": type(exc).__name__,
                "restconf.response.payload": None,
            }},
        )
        raise

    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    outcome = "success" if response.ok else "failure"
    try:
        response_payload = response.json()
    except ValueError:
        response_payload = response.text
    current_app.logger.info(
        "RESTCONF %s %s %.2fms",
        response.status_code,
        metric,
        duration_ms,
        extra={"event_fields": {
            **fields,
            "event.action": "restconf_response",
            "event.outcome": outcome,
            "http.response.status_code": response.status_code,
            "event.duration_ms": duration_ms,
            "restconf.response.payload": response_payload,
        }},
    )
    response.raise_for_status()
    return response


def collect(router, password):
    request_options = {
        "headers": {"Accept": "application/yang-data+json"},
        "auth": (router.username, password),
        "timeout": (5, 15),
        "verify": False,
    }
    cpu_response = _restconf_get(router, CPU_PATH, "cpu", request_options)
    memory_response = _restconf_get(router, MEMORY_PATH, "memory", request_options)

    cpu = _find(cpu_response.json(), {"five-seconds", "five_seconds", "cpu-utilization", "value"})
    used = _find(memory_response.json(), {"used-memory", "used_memory", "used"})
    total = _find(memory_response.json(), {"total-memory", "total_memory", "total"})
    free = _find(memory_response.json(), {"free-memory", "free_memory", "free"})
    if used is None and total is not None and free is not None:
        used = total - free
    if total is None and used is not None and free is not None:
        total = used + free
    if cpu is None or used is None or not total:
        raise ValueError("expected CPU or memory leaves not found")
    return {
        "cpu_percent": round(cpu, 2),
        "memory_percent": round(used / total * 100, 2),
    }
