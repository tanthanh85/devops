from flask import Flask

from .config import Config
from .loopbacks import loopback_api
from .models import db
from .observability import configure_observability
from .routes import api


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)
    configure_observability(app)
    db.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(loopback_api)
    with app.app_context():
        db.create_all()
    return app

