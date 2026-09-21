from __future__ import annotations

from datetime import datetime, timezone
import json
import logging
import os
import time
import uuid

from flask import g, request


class JsonFormatter(logging.Formatter):
    def format(self, record):
        event = {
            "@timestamp": datetime.now(timezone.utc).isoformat(),
            "log.level": record.levelname.lower(),
            "message": record.getMessage(),
            "service.name": "network-monitor-app",
            "service.type": "application",
            "container.name": "network-monitor-app",
            "event.dataset": "network_monitor.application",
            "kubernetes.pod.name": os.getenv("POD_NAME", os.getenv("HOSTNAME", "unknown")),
            "kubernetes.pod.ip": os.getenv("POD_IP", "unknown"),
            "kubernetes.node.name": os.getenv("NODE_NAME", "unknown"),
        }
        supplied = getattr(record, "event_fields", None)
        if isinstance(supplied, dict):
            event.update(supplied)
        return json.dumps(event, separators=(",", ":"), default=str)


def configure_observability(app):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    app.logger.handlers.clear()
    app.logger.addHandler(handler)
    app.logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    app.logger.propagate = False

    @app.before_request
    def start_request_timer():
        g.request_started = time.perf_counter()
        g.request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))[:64]

    @app.after_request
    def log_request(response):
        duration_ms = round((time.perf_counter() - g.request_started) * 1000, 2)
        fields = {
            "event.action": "http_request",
            "event.outcome": "success" if response.status_code < 400 else "failure",
            "http.request.method": request.method,
            "http.response.status_code": response.status_code,
            "http.response.body.bytes": response.calculate_content_length() or 0,
            "url.path": request.path,
            "event.duration_ms": duration_ms,
            "trace.id": g.request_id,
            "user.id": str(getattr(g, "user_id", "anonymous")),
        }
        if request.endpoint == "api.router_metrics" and response.is_json:
            payload = response.get_json(silent=True) or {}
            if response.status_code == 200:
                fields.update({
                    "event.action": "router_metric_collection",
                    "network.router.name": payload.get("router"),
                    "network.router.cpu.pct": payload.get("cpu_percent"),
                    "network.router.memory.pct": payload.get("memory_percent"),
                })
        app.logger.info("request completed", extra={"event_fields": fields})
        response.headers["X-Request-ID"] = g.request_id
        return response
