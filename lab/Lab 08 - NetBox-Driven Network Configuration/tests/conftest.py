import os
from cryptography.fernet import Fernet

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["INVENTORY_ENCRYPTION_KEY"] = Fernet.generate_key().decode()
os.environ["FLASK_SECRET_KEY"] = "test-secret"
os.environ["NETBOX_URL"] = "https://netbox.test"
os.environ["NETBOX_API_TOKEN"] = "test-netbox-token"
os.environ["NETBOX_ROUTER_USERNAME"] = "student"
os.environ["NETBOX_ROUTER_PASSWORD"] = "secret-value"

import pytest
from app import create_app
from app.models import db


@pytest.fixture()
def client():
    app=create_app(); app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all(); db.create_all()
    return app.test_client()
