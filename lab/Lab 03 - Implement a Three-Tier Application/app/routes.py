from datetime import datetime, timezone
import ipaddress
import re

from flask import Blueprint, jsonify, request, session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from .models import Router, User, db
from .restconf_client import collect
from .security import admin_required, decrypt, encrypt, login_required

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
    return jsonify(items=[{"id":r.id,"name":r.name,"host":r.host,"port":r.port,"username":r.username,"enabled":r.enabled} for r in Router.query.order_by(Router.name)])


@api.post("/api/routers")
@admin_required
def add_router():
    data=body(); host=str(data.get("host", "")).strip(); name=str(data.get("name", "")).strip(); password=str(data.get("password", ""))
    try:
        if not host or not name or not password: raise ValueError("name, host, and password are required")
        try: ipaddress.ip_address(host)
        except ValueError:
            if not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", host): raise ValueError("invalid host")
        port=int(data.get("port",443))
        if not 1 <= port <= 65535: raise ValueError("invalid port")
        router=Router(name=name,host=host,port=port,username=str(data.get("username", "")),password_ciphertext=encrypt(password),enabled=bool(data.get("enabled",True)))
        db.session.add(router); db.session.commit()
        return jsonify(id=router.id,status="created"),201
    except (ValueError, IntegrityError) as exc:
        db.session.rollback(); return jsonify(error=str(exc)),422


@api.delete("/api/routers/<int:router_id>")
@admin_required
def delete_router(router_id):
    router=db.session.get(Router,router_id)
    if not router: return jsonify(error="router not found"),404
    db.session.delete(router); db.session.commit(); return ("",204)


@api.get("/api/routers/<int:router_id>/metrics")
@login_required
def router_metrics(router_id):
    router=db.session.get(Router,router_id)
    if not router or not router.enabled: return jsonify(error="router unavailable"),404
    try:
        values=collect(router,decrypt(router.password_ciphertext))
        return jsonify(router=router.name,timestamp=datetime.now(timezone.utc).isoformat(),**values)
    except Exception as exc:
        return jsonify(error=f"collection failed: {type(exc).__name__}"),502
