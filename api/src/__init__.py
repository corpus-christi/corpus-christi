from flask import Flask
from flask_jwt_extended import JWTManager

from config import config
from .db import DbConfig

db = DbConfig()
jwt = JWTManager()


def create_app(config_name):
    """Application factory for the API."""

    # Initialize application.
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Set up the database.
    db.init_app(app)

    # Configure JSON Web Tokens
    jwt.init_app(app)

    # Attached CC modules
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/v1/auth')

    from .etc import etc as etc_blueprint
    app.register_blueprint(etc_blueprint, url_prefix='/')

    from .events import events as events_blueprint
    app.register_blueprint(events_blueprint, url_prefix='/api/v1/events')

    from .groups import groups as groups_blueprint
    app.register_blueprint(groups_blueprint, url_prefix='/api/v1/groups')

    from .i18n import i18n as i18n_blueprint
    app.register_blueprint(i18n_blueprint, url_prefix='/api/v1/i18n')

    from .people import people as people_blueprint
    app.register_blueprint(people_blueprint, url_prefix='/api/v1/people')

    from .places import places as places_blueprint
    app.register_blueprint(places_blueprint, url_prefix='/api/v1/places')

    from .roles import roles as roles_blueprint
    app.register_blueprint(roles_blueprint, url_prefix='/api/v1/roles')

    return app
