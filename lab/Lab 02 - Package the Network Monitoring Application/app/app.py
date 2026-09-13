from flask import Flask, jsonify, render_template

from .config import Settings
from .metrics_service import sample
from .restconf_client import RestconfClient, RestconfError


app = Flask(__name__)
settings = Settings()
client = RestconfClient(settings)


@app.get("/")
def dashboard():
    return render_template("dashboard.html", router=settings.router_host, mock=settings.mock_mode)


@app.get("/health")
def health():
    return jsonify(status="healthy")


@app.get("/api/metrics")
def metrics():
    try:
        return jsonify(sample(settings, client))
    except (RestconfError, ValueError) as exc:
        app.logger.warning("Metric collection failed: %s", exc)
        return jsonify(error=str(exc)), 502
