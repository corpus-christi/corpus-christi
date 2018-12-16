import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret key'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'dev-db.sqlite')


class TestingConfig(Config):
    TESTING = True
    # SQLALCHEMY_ECHO = True        # Really chatty.

    if True:
        # SQLite
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or \
                                  'sqlite:///' + os.path.join(basedir, 'test-db.sqlite')
    else:
        # PostgreSQL
        SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or \
                                  'postgresql://tom@localhost:5432/cc-test'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DB_URL') or \
                              'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'prod': ProductionConfig,

    'default': DevelopmentConfig
}
