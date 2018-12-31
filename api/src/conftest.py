import os

import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from . import db, create_app


class CustomClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self.db = db
        self.sqla = db.session
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        access_token = create_access_token(identity='test-user')
        kwargs['headers'] = {"AUTHORIZATION": f"Bearer {access_token}"}
        return super().open(*args, **kwargs)


@pytest.fixture
def client():
    """Create a Flask test client."""
    app = create_app(os.getenv('FLASK_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out
    app.test_client_class = CustomClient

    db.drop_all()
    db.create_all()

    with app.test_request_context():
        with app.test_client() as client:
            yield client

