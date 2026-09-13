from collections import deque
from datetime import datetime, timezone
import hmac
import os

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
events = deque(maxlen=int(os.getenv("MAX_EVENTS", "200")))


def authorized():
    expected = os.getenv("WEBHOOK_TOKEN", "")
    supplied = request.headers.get("X-Webhook-Token", "")
    return bool(expected) and hmac.compare_digest(expected, supplied)


@app.get("/health")
def health():
    return jsonify(status="healthy")


@app.post("/webhook/elastic")
def receive_alert():
    if not authorized():
        return jsonify(error="unauthorized"), 401
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="JSON object required"), 400
    event = {
        "received_at": datetime.now(timezone.utc).isoformat(),
        "rule_name": str(payload.get("rule_name", "Unnamed rule"))[:160],
        "status": str(payload.get("status", "unknown"))[:32],
        "severity": str(payload.get("severity", "warning"))[:32],
        "reason": str(payload.get("reason", "No reason supplied"))[:500],
        "value": payload.get("value"),
        "threshold": payload.get("threshold"),
        "group": str(payload.get("group", "all"))[:160],
    }
    events.appendleft(event)
    app.logger.info("accepted Elastic alert rule=%s status=%s", event["rule_name"], event["status"])
    return jsonify(status="accepted"), 202


@app.get("/api/events")
def list_events():
    return jsonify(items=list(events))


@app.get("/")
def index():
    return render_template("index.html")

