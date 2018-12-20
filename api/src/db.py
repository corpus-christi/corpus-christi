from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DbConfig:
    def __init__(self):
        self.engine = None
        self.session = None

    def init_app(self, app):
        self.engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_all(self):
        """Create all tables."""
        Base.metadata.create_all(self.engine)

    def drop_all(self):
        """Drop all tables"""
        Base.metadata.drop_all(self.engine)
