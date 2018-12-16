from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import config

# These constructors return otherwise unconfigured instances
# that are then set up in the `create_app` function.
orm = SQLAlchemy()
migrate = Migrate()
marm = Marshmallow()


def create_app(config_name):
    """Application factor for the API."""

    # Initialize application.
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize previously constructed packages
    orm.init_app(app)
    migrate.init_app(app, orm)
    marm.init_app(app)  # Must be AFTER db.init_app

    # Attached CC modules
    from .gather import gather as gather_blueprint
    app.register_blueprint(gather_blueprint, url_prefix='/api/v1/gather')

    from .i18n import i18n as i18n_blueprint
    app.register_blueprint(i18n_blueprint, url_prefix='/api/v1/i18n')

    from .etc import etc as etc_blueprint
    app.register_blueprint(etc_blueprint, url_prefix='/')

    return app
