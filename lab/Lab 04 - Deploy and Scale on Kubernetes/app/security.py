from functools import wraps

from flask import jsonify, session


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
