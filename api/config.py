import datetime
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLITE_TEST = 'sqlite:///' + os.path.join(BASE_DIR, 'test-db.sqlite')
SQLITE_DEV = 'sqlite:///' + os.path.join(BASE_DIR, 'dev-db.sqlite')
SQLITE_MEM = 'sqlite://'

PSQL_TEST = 'postgresql://tom@localhost:5432/cc-test'
PSQL_DEV = 'postgresql://tom@localhost:5432/cc-dev'
PSQL_PROD = 'postgresql://tom@localhost:5432/cc-prod'


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'flask super secret key'

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt super secret key'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=8)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    # SQLALCHEMY_ECHO = True        # Really chatty.
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or SQLITE_TEST


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or SQLITE_DEV


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DB_URL') or PSQL_PROD


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
