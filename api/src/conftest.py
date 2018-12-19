import os

import pytest

from src.db import Base
from . import db as _db, create_app


@pytest.fixture()
def app():
    """Create an app instance configured for testing."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out
    return app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    with app.test_request_context():
        with app.test_client() as client:
            yield client


@pytest.fixture()
def dbs(app):
    """Inject a database session."""
    return _db.session

