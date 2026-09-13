import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "development-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:////tmp/network-monitor.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
    VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault:8200")
    VAULT_CACERT = os.getenv("VAULT_CACERT", "")
    VAULT_KV_MOUNT = os.getenv("VAULT_KV_MOUNT", "secret")
    VAULT_KUBERNETES_ROLE = os.getenv("VAULT_KUBERNETES_ROLE", "network-monitor")
    KUBERNETES_TOKEN_PATH = os.getenv(
        "KUBERNETES_TOKEN_PATH",
        "/var/run/secrets/kubernetes.io/serviceaccount/token",
    )

