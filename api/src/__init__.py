from flask import Flask
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from config import config, BASE_DIR
from .db import DbConfig

db = DbConfig()
jwt = JWTManager()
mail = Mail()

BASE_DIR = BASE_DIR


def create_app(config_name):
    """Application factory for the API."""
    print("config_name = ", config_name)
    #  Initialize application.
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Set up the mailing service.
    mail.init_app(app)

    # Set up the database.
    db.init_app(app)

    # Configure JSON Web Tokens
    jwt.init_app(app)

    # Attached CC modules
    from .attributes import attributes as attributes_blueprint
    app.register_blueprint(attributes_blueprint,
                           url_prefix='/api/v1/attributes')

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/v1/auth')

    from .etc import etc as etc_blueprint
    app.register_blueprint(etc_blueprint, url_prefix='/')

    from .events import events as events_blueprint
    app.register_blueprint(events_blueprint, url_prefix='/api/v1/events')

    from .assets import assets as assets_blueprint
    app.register_blueprint(assets_blueprint, url_prefix='/api/v1/assets')

    from .teams import teams as teams_blueprint
    app.register_blueprint(teams_blueprint, url_prefix='/api/v1/teams')

    from .emails import emails as emails_blueprint
    app.register_blueprint(emails_blueprint, url_prefix='/api/v1/emails')

    from .groups import groups as groups_blueprint
    app.register_blueprint(groups_blueprint, url_prefix='/api/v1/groups')

    from .courses import courses as courses_blueprint
    app.register_blueprint(courses_blueprint, url_prefix='/api/v1/courses')

    from .i18n import i18n as i18n_blueprint
    app.register_blueprint(i18n_blueprint, url_prefix='/api/v1/i18n')

    from .people import people as people_blueprint
    app.register_blueprint(people_blueprint, url_prefix='/api/v1/people')

    from .places import places as places_blueprint
    app.register_blueprint(places_blueprint, url_prefix='/api/v1/places')

    from .images import images as images_blueprint
    app.register_blueprint(images_blueprint, url_prefix='/api/v1/images')

    return app
