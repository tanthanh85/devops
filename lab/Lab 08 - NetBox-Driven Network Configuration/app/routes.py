from datetime import datetime, timezone
import hmac
import re
import socket

from flask import Blueprint, current_app, jsonify, request, session
import requests
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from .models import Router, SyntheticConfig, SyntheticResult, User, db
from .netbox_client import fetch_devices
from .restconf_client import collect, collect_loopbacks
from .security import admin_required, decrypt, encrypt, login_required

api = Blueprint("api", __name__)
SYNTHETIC_INTERVALS = {30, 60, 120, 300, 600, 1800}


def body():
    value = request.get_json(silent=True)
    return value if isinstance(value, dict) else {}


def synthetic_runner_authorized():
    supplied = request.headers.get("X-Synthetic-Token", "")
    expected = current_app.config["SECRET_KEY"]
    return bool(supplied) and hmac.compare_digest(supplied, expected)


def result_json(result):
    if result is None:
        return None
    return {
        "outcome": result.outcome,
        "status_code": result.status_code,
        "response_time_ms": result.response_time_ms,
        "error_message": result.error_message,
        "timestamp": result.created_at.replace(tzinfo=timezone.utc).isoformat(),
    }


@api.get("/health/live")
def live(): return jsonify(status="alive")


@api.get("/health/ready")
def ready():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify(status="ready")
    except Exception:
        return jsonify(status="not-ready"), 503


@api.get("/api/instance")
def instance():
    return jsonify(tier="app", instance=socket.gethostname())


@api.get("/api/setup/status")
def setup_status(): return jsonify(setup_required=User.query.first() is None)


@api.post("/api/setup/admin")
def setup_admin():
    data = body(); username = str(data.get("username", "")).strip().lower(); password = str(data.get("password", ""))
    if not re.fullmatch(r"[a-z][a-z0-9_.-]{2,31}", username): return jsonify(error="invalid username"), 422
    if not password: return jsonify(error="password is required"), 422
    try:
        if User.query.with_for_update().first() is not None: return jsonify(error="setup already completed"), 409
        # Reserving identifier 1 makes concurrent first-use inserts contend on
        # the same database constraint even when the table was initially empty.
        user = User(id=1, username=username, is_admin=True); user.set_password(password)
        db.session.add(user); db.session.commit()
        return jsonify(status="created"), 201
    except IntegrityError:
        db.session.rollback(); return jsonify(error="setup already completed"), 409


@api.get("/api/synthetic/config")
@admin_required
def synthetic_config():
    config = db.session.get(SyntheticConfig, 1)
    results = SyntheticResult.query.order_by(SyntheticResult.created_at.desc()).limit(30).all()
    return jsonify(
        configured=config is not None,
        username=config.username if config else "",
        interval_seconds=config.interval_seconds if config else 120,
        enabled=config.enabled if config else False,
        last_result=result_json(results[0]) if results else None,
        results=[result_json(item) for item in reversed(results)],
    )


@api.post("/api/synthetic/config")
@admin_required
def save_synthetic_config():
    data = body()
    username = str(data.get("username", "")).strip().lower()
    password = str(data.get("password", ""))
    try:
        interval_seconds = int(data.get("interval_seconds", 120))
        if not re.fullmatch(r"[a-z][a-z0-9_.-]{2,31}", username):
            raise ValueError("invalid synthetic username")
        if not password:
            raise ValueError("synthetic password is required")
        if interval_seconds not in SYNTHETIC_INTERVALS:
            raise ValueError("invalid synthetic interval")
        user = User.query.filter_by(username=username).first()
        if user and user.is_admin:
            raise ValueError("use a separate non-administrator account")
        if user is None:
            user = User(username=username, is_admin=False)
            db.session.add(user)
        user.set_password(password)
        config = db.session.get(SyntheticConfig, 1)
        if config is None:
            config = SyntheticConfig(id=1, username=username, password_ciphertext=encrypt(password))
            db.session.add(config)
        config.username = username
        config.password_ciphertext = encrypt(password)
        config.interval_seconds = interval_seconds
        config.enabled = True
        config.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify(status="saved", username=username, interval_seconds=interval_seconds)
    except (ValueError, IntegrityError) as exc:
        db.session.rollback()
        return jsonify(error=str(exc)), 422


@api.get("/api/internal/synthetic/config")
def internal_synthetic_config():
    if not synthetic_runner_authorized():
        return jsonify(error="unauthorized"), 401
    config = db.session.get(SyntheticConfig, 1)
    if config is None or not config.enabled:
        return jsonify(configured=False)
    return jsonify(
        configured=True,
        username=config.username,
        password=decrypt(config.password_ciphertext),
        interval_seconds=config.interval_seconds,
        version=config.updated_at.replace(tzinfo=timezone.utc).isoformat(),
    )


@api.post("/api/internal/synthetic/results")
def record_synthetic_result():
    if not synthetic_runner_authorized():
        return jsonify(error="unauthorized"), 401
    data = body()
    outcome = str(data.get("outcome", ""))
    if outcome not in {"success", "failure"}:
        return jsonify(error="invalid outcome"), 422
    try:
        response_time_ms = max(0, float(data.get("response_time_ms")))
        status_code = data.get("status_code")
        result = SyntheticResult(
            outcome=outcome,
            status_code=int(status_code) if status_code is not None else None,
            response_time_ms=response_time_ms,
            error_message=str(data.get("error_message", ""))[:255] or None,
        )
        db.session.add(result)
        db.session.commit()
        return jsonify(status="recorded"), 201
    except (TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify(error=str(exc)), 422


@api.post("/api/session")
def login():
    data=body(); user=User.query.filter_by(username=str(data.get("username", "")).strip().lower()).first()
    if not user or not user.verify_password(str(data.get("password", ""))): return jsonify(error="invalid credentials"), 401
    session.clear(); session.update(user_id=user.id, is_admin=user.is_admin)
    return jsonify(status="authenticated", username=user.username)


@api.get("/api/session")
def session_status():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify(authenticated=False)
    user = db.session.get(User, user_id)
    if user is None:
        session.clear()
        return jsonify(authenticated=False)
    return jsonify(authenticated=True, username=user.username, is_admin=user.is_admin)


@api.delete("/api/session")
def logout(): session.clear(); return ("", 204)


@api.get("/api/routers")
@login_required
def list_routers():
    return jsonify(items=[{"id":r.id,"name":r.name,"host":r.host,"port":r.port,"enabled":r.enabled} for r in Router.query.filter_by(enabled=True).order_by(Router.name)])


@api.post("/api/inventory/netbox")
@admin_required
def sync_netbox_inventory():
    try:
        username = current_app.config["NETBOX_ROUTER_USERNAME"]
        password = current_app.config["NETBOX_ROUTER_PASSWORD"]
        if not username or not password:
            raise RuntimeError("router automation credentials are not configured")
        devices = fetch_devices()
        active_names = set()
        for item in devices:
            active_names.add(item["name"])
            router = Router.query.filter_by(name=item["name"]).first()
            if router is None:
                router = Router(name=item["name"])
                db.session.add(router)
            router.host = item["host"]
            router.port = item["port"]
            router.username = username
            router.password_ciphertext = encrypt(password)
            router.enabled = True
        for router in Router.query.all():
            if router.name not in active_names:
                router.enabled = False
        db.session.commit()
        return jsonify(status="synchronized", imported=len(devices), items=devices)
    except (requests.RequestException, RuntimeError, ValueError, KeyError) as exc:
        db.session.rollback()
        return jsonify(error=f"NetBox synchronization failed: {type(exc).__name__}"), 502


@api.get("/api/routers/<int:router_id>/metrics")
@login_required
def router_metrics(router_id):
    router=db.session.get(Router,router_id)
    if not router or not router.enabled: return jsonify(error="router unavailable"),404
    try:
        values=collect(router,decrypt(router.password_ciphertext))
        return jsonify(app_instance=socket.gethostname(),router=router.name,timestamp=datetime.now(timezone.utc).isoformat(),**values)
    except Exception as exc:
        return jsonify(error=f"collection failed: {type(exc).__name__}"),502


@api.get("/api/routers/<int:router_id>/loopbacks")
@login_required
def router_loopbacks(router_id):
    router = db.session.get(Router, router_id)
    if not router or not router.enabled:
        return jsonify(error="router unavailable"), 404
    try:
        interfaces = collect_loopbacks(router, decrypt(router.password_ciphertext))
        return jsonify(router=router.name, items=interfaces)
    except Exception as exc:
        return jsonify(error=f"loopback collection failed: {type(exc).__name__}"), 502
