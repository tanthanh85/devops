from functools import wraps

from cryptography.fernet import Fernet
from flask import current_app, jsonify, session


def cipher():
    key = current_app.config["INVENTORY_ENCRYPTION_KEY"]
    if not key:
        raise RuntimeError("INVENTORY_ENCRYPTION_KEY is required")
    return Fernet(key.encode())


def encrypt(value: str) -> str:
    return cipher().encrypt(value.encode()).decode()


def decrypt(value: str) -> str:
    return cipher().decrypt(value.encode()).decode()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error="authentication required"), 401
        return function(*args, **kwargs)
    return wrapper


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify(error="authentication required"), 401
        if not session.get("is_admin"):
            return jsonify(error="administrator access required"), 403
        return function(*args, **kwargs)
    return wrapper
