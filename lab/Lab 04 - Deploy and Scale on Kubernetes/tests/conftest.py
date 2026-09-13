import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["FLASK_SECRET_KEY"] = "test-secret"

import pytest
from app import create_app
from app.models import db


@pytest.fixture()
def client():
    app=create_app(); app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all(); db.create_all()
    return app.test_client()
