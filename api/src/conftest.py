import os

import pytest
from flask import url_for
from flask_jwt_extended import create_access_token

from . import db as _db, create_app
from .people.models import Person, Account


def create_test_account(client, db, username, password):
    # Create a test account.

    person = Person(first_name='Test', last_name='User')
    account = Account(username=username, password=password, person=person)
    db.session.add(account)
    db.session.commit()

    # Authenticate against it; return the token.
    resp = client.post(url_for('auth.login'), json={'username': username, 'password': password})
    print("\nLOGIN RESP", resp.json)
    return resp.json['jwt']

    # return create_access_token(identity='test')



@pytest.fixture()
def app():
    """Create an app instance configured for testing."""
    print("\nGET APP")
    app = create_app(os.getenv('FLASK_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out
    return app


@pytest.fixture
def client(db, app):
    """Create a Flask test client."""
    print("\nCREATE CLIENT")
    with app.test_request_context():
        with app.test_client() as client:
            access_token = create_test_account(client, db, 'test', 'password')
            client.environ_base['AUTHORIZATION'] = f"Bearer {access_token}"
            print("TOKEN", access_token)
            yield client


@pytest.fixture()
def reset_db(app):
    """Reset the database."""
    print("\nCLOBBER DATABASE")
    _db.drop_all()
    _db.create_all()


@pytest.fixture()
def db(reset_db):
    """Inject a database session."""
    print("\nGET DATABASE")
    return _db
