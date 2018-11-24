from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()


def create_app(config_name):
    # Initialize application.
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize Python packages
    db.init_app(app)

    # Attached CC modules
    from .gather import gather as gather_blueprint
    app.register_blueprint(gather_blueprint)

    return app
