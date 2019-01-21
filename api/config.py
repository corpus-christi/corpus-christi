import datetime
import os
try:
    import private
except:
    print("Private.py not needed for CI testing")

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

SQLITE_TEST = 'sqlite:///' + os.path.join(BASE_DIR, 'test-db.sqlite')
SQLITE_DEV = 'sqlite:///' + os.path.join(BASE_DIR, 'dev-db.sqlite')
SQLITE_MEM = 'sqlite://'

PSQL_TEST = 'postgresql://arco@localhost:5432/cc-test'
PSQL_DEV = 'postgresql://arco@localhost:5432/cc-dev'
try:
    PSQL_STAGING = 'postgresql://arco:' + private.PASS + '@localhost:5432/cc-staging'
except:
    print("Private.py not needed for CI testing")
PSQL_STAGING_CI = 'postgresql://arco@localhost:5432/cc-staging'
PSQL_PROD = 'postgresql://arco@localhost:5432/cc-prod'


class Config:
    try:
        SECRET_KEY = os.environ.get(private.SECRET_KEY1) or private.SECRET_KEY2
    except: 
        print("Private.py not needed for CI testing")

    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt super secret key'
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=8)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or SQLITE_TEST


class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or SQLITE_DEV


class StagingConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or PSQL_STAGING

class StagingConfigCI(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or PSQL_STAGING_CI

class ProductionConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DB_URL') or PSQL_PROD


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'staging': StagingConfig,
    'staging-ci': StagingConfigCI,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
