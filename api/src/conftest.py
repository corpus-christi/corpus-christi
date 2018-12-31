import os

import pytest
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from . import db, create_app


class AuthClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self.sqla = db.session
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        access_token = create_access_token(identity='test-user')
        kwargs['headers'] = {"AUTHORIZATION": f"Bearer {access_token}"}
        return super().open(*args, **kwargs)


def client_factory(client_class):
    app = create_app(os.getenv('FLASK_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out
    app.test_client_class = client_class

    db.drop_all()
    db.create_all()

    with app.test_request_context():
        with app.test_client() as client:
            yield client


@pytest.fixture
def auth_client():
    yield from client_factory(AuthClient)


@pytest.fixture
def plain_client():
    yield from client_factory(FlaskClient)
