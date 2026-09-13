import os
from pathlib import Path
import sys

import pytest


lab_root = Path(__file__).resolve().parents[2]
for source in (
    lab_root / "Lab 04 - Deploy and Scale on Kubernetes",
    lab_root / "Lab 06 - Monitor with the Elastic Stack",
    Path(__file__).resolve().parents[1],
):
    sys.path.insert(0, str(source))

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["FLASK_SECRET_KEY"] = "test-secret"

from app import create_app
from app.models import db


@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app.test_client()
