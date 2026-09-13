from flask import Blueprint, current_app, jsonify

from .netbox_client import list_loopbacks
from .security import login_required

loopback_api = Blueprint("loopback_api", __name__)


@loopback_api.get("/api/loopbacks")
@login_required
def loopbacks():
    try:
        items = list_loopbacks()
        current_app.logger.info("NetBox loopback inventory retrieved", extra={"event_fields": {"event.action": "netbox_loopback_read", "netbox.loopback.count": len(items)}})
        return jsonify(items=items)
    except Exception as exc:
        current_app.logger.warning("NetBox loopback read failed: %s", type(exc).__name__)
        return jsonify(error="NetBox loopback inventory unavailable"), 502

