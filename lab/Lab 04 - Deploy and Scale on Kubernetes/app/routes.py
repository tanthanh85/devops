from datetime import datetime, timezone
import re

from flask import Blueprint, current_app, jsonify, request, session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from .models import User, db
from .restconf_client import collect
from .security import login_required
from .vault_client import list_routers as vault_list_routers, read_router

api = Blueprint("api", __name__)


def body():
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else {}


@api.get("/health/live")
def live(): return jsonify(status="alive")


@api.get("/health/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ready")
    except Exception:
        return jsonify(status="not-ready"), 503


@api.get("/api/setup/status")
def setup_status(): return jsonify(setup_required=User.query.first() is None)


@api.post("/api/setup/admin")
def setup_admin():
    data = body(); username = str(data.get("username", "")).strip().lower(); password = str(data.get("password", ""))
    if not re.fullmatch(r"[a-z][a-z0-9_.-]{2,31}", username): return jsonify(error="invalid username"), 422
    if len(password) < 12: return jsonify(error="password must contain at least 12 characters"), 422
    try:
        if User.query.with_for_update().first() is not None: return jsonify(error="setup already completed"), 409
        user = User(id=1, username=username, is_admin=True); user.set_password(password)
        db.session.add(user); db.session.commit()
        return jsonify(status="created"), 201
    except IntegrityError:
        db.session.rollback(); return jsonify(error="setup already completed"), 409


@api.post("/api/session")
def login():
    data=body(); user=User.query.filter_by(username=str(data.get("username", "")).strip().lower()).first()
    if not user or not user.verify_password(str(data.get("password", ""))): return jsonify(error="invalid credentials"), 401
    session.clear(); session.update(user_id=user.id, is_admin=user.is_admin)
    return jsonify(status="authenticated", username=user.username)


@api.delete("/api/session")
def logout(): session.clear(); return ("", 204)


@api.get("/api/routers")
@login_required
def list_routers():
    try:
        return jsonify(items=vault_list_routers())
    except Exception as exc:
        current_app.logger.warning("Vault inventory read failed: %s", type(exc).__name__)
        return jsonify(error="router inventory unavailable"), 502


@api.get("/api/routers/<string:router_name>/metrics")
@login_required
def router_metrics(router_name):
    try:
        router = read_router(router_name)
        if not router.enabled:
            return jsonify(error="router unavailable"), 404
        values = collect(router)
        return jsonify(router=router.name,timestamp=datetime.now(timezone.utc).isoformat(),**values)
    except Exception as exc:
        current_app.logger.warning("metric collection failed for Vault router %s: %s", router_name, type(exc).__name__)
        return jsonify(error=f"collection failed: {type(exc).__name__}"),502
