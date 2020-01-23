import datetime
import os
import sys
from contextlib import redirect_stdout

try:
    import private
except ImportError:
    with redirect_stdout(sys.stderr):
        print("Can't find 'private.py' configuration file")
        sys.exit(1)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def psql_url(db_config):
    url_prefix = f'postgresql://{private.PSQL_USER}:{private.PSQL_PASS}@{private.PSQL_HOST}/'

    if  hasattr(private, "PSQL_DB"):
        return url_prefix + private.PSQL_DB
    elif db_config == 'test':
        return url_prefix + 'cc-test'
    elif db_config == 'dev':
        return url_prefix + 'cc-dev'
    elif db_config == 'staging':
        return url_prefix + 'cc-staging'
    elif db_config == 'prod':
        return url_prefix + 'cc-prod'
    else:
        raise RuntimeError(f"Can't determine Postgres URL with dbconfig '{db_config}'")


class Config:
    SECRET_KEY = os.environ.get(private.FLASK_SECRET_KEY) or private.FLASK_SECRET_KEY

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or private.JWT_SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=8)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    try:
        MAIL_USERNAME = private.EMAIL_USERNAME
        MAIL_PASSWORD = private.EMAIL_PASSWORD
    except AttributeError:
        MAIL_USERNAME = ""
        MAIL_PASSWORD = ""

    MAIL_SUPPRESS_SEND = False

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or psql_url('test')
    JWT_BLACKLIST_ENABLED = False


class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or psql_url('dev')


class StagingConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or psql_url('staging')


class ProductionConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DB_URL') or psql_url('prod')


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'staging': StagingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
