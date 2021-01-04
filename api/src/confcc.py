import datetime
import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY")

    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=8)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USERNAME = os.getenv("EMAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_SUPPRESS_SEND = False

    @staticmethod
    def init_app(app):
        pass

    @staticmethod
    def psql_url(db_config):
        url_prefix = "".join(
            ["postgresql://",
             os.getenv("PSQL_USER"), ":",
             os.getenv("PSQL_PASS"), "@",
             os.getenv("PSQL_HOST"), "/"
             ])

        if os.getenv("PSQL_DB") is not None:
            return url_prefix + os.getenv("PSQL_DB")
        elif db_config == 'test':
            return url_prefix + 'cc-test'
        elif db_config == 'dev':
            return url_prefix + 'cc-dev'
        elif db_config == 'staging':
            return url_prefix + 'cc-staging'
        elif db_config == 'prod':
            return url_prefix + 'cc-prod'
        else:
            raise RuntimeError(
                f"Can't determine Postgres URL for dbconfig '{db_config}'")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DB_URL') or Config.psql_url('test')
    JWT_BLACKLIST_ENABLED = False


class DevelopmentConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DB_URL') or Config.psql_url('dev')


class StagingConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DB_URL') or Config.psql_url('staging')


class ProductionConfig(Config):
    TESTING = False
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('PROD_DB_URL') or Config.psql_url('prod')


config = {
    'dev': DevelopmentConfig,
    'test': TestingConfig,
    'staging': StagingConfig,
    'prod': ProductionConfig,
    'default': DevelopmentConfig
}
