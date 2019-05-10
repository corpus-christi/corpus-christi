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

PSQL_COMMON = f'postgresql://{private.PSQL_USER}:{private.PSQL_PASS}@{private.PSQL_HOST}/'
PSQL_TEST = PSQL_COMMON + 'cc-test'
PSQL_DEV = PSQL_COMMON + 'cc-dev'
PSQL_STAGING = PSQL_COMMON + 'cc-staging'
PSQL_PROD = PSQL_COMMON + 'cc-prod'


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
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or PSQL_TEST
    JWT_BLACKLIST_ENABLED = False


class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or PSQL_DEV


class StagingConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or PSQL_STAGING


class ProductionConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DB_URL') or PSQL_PROD


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'staging': StagingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
