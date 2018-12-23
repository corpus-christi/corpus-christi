from flask_migrate import Migrate
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()


class DbConfig:
    def __init__(self):
        self.engine = None
        self.session = None

    def init_app(self, app):
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        session_factory = sessionmaker(bind=self.engine)
        self.session = scoped_session(session_factory)

        # We're only using this package to get the CLI command.
        Migrate(app, Base)

        @app.teardown_appcontext
        def remove_session(exc):
            self.session.remove()

    def create_all(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        """Drop all tables"""
        Base.metadata.drop_all(self.engine)
