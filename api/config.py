import datetime
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLITE_TEST = 'sqlite:///' + os.path.join(BASE_DIR, 'test-db.sqlite')
SQLITE_DEV = 'sqlite:///' + os.path.join(BASE_DIR, 'dev-db.sqlite')
SQLITE_MEM = 'sqlite://'

PSQL_TEST = 'postgresql://tom@localhost:5432/cc-test'
PSQL_DEV = 'postgresql://tom@localhost:5432/cc-dev'
PSQL_STAGING = 'postgresql://tom@localhost:5432/cc-staging'
PSQL_PROD = 'postgresql://tom@localhost:5432/cc-prod'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flask super secret key'

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt super secret key'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=8)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('EMAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    MAIL_SUPPRESS_SEND = False

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or SQLITE_TEST
    JWT_BLACKLIST_ENABLED = False

class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or SQLITE_DEV


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
