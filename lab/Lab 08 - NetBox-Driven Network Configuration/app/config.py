import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:////tmp/network-monitor.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    NETBOX_URL = os.environ.get("NETBOX_URL", "")
    NETBOX_API_TOKEN = os.environ.get("NETBOX_API_TOKEN", "")
    NETBOX_VERIFY_TLS = os.environ.get("NETBOX_SKIP_TLS_VERIFY", "false").lower() != "true"
    NETBOX_ROUTER_USERNAME = os.environ.get("NETBOX_ROUTER_USERNAME", "")
    NETBOX_ROUTER_PASSWORD = os.environ.get("NETBOX_ROUTER_PASSWORD", "")
    INVENTORY_ENCRYPTION_KEY = os.getenv("INVENTORY_ENCRYPTION_KEY", "")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
