import os

import pytest

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
def reset_db():
    _db.drop_all()
    _db.create_all()


@pytest.fixture()
def dbs(reset_db):
    """Inject a database session."""
    return _db.session
