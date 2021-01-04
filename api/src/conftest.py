import logging
import os

from dotenv import load_dotenv

load_dotenv()

import pytest
from .cli.app import create_app_cli
from .cli.courses import create_course_cli
from .cli.events import create_event_cli
from .cli.faker import create_faker_cli
from .cli.i18n import create_i18n_cli
from .cli.people import create_account_cli
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token

from . import db, create_app


class AuthClient(FlaskClient):
    def __init__(self, *args, **kwargs):
        self.sqla = db.session
        super().__init__(*args, **kwargs)

    def open(self, *args, **kwargs):
        if 'headers' not in kwargs:
            from .people.models import Person, PersonSchema
            from .people.test_people import person_object_factory
            test_person = Person(
                **PersonSchema().load(person_object_factory()))
            test_person.username = 'test-user'
            access_token = create_access_token(identity=test_person)
            kwargs['headers'] = {"AUTHORIZATION": f"Bearer {access_token}"}
        return super().open(*args, **kwargs)


def client_factory(client_class):
    app = create_app(os.getenv('CC_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out
    app.test_client_class = client_class
    logging.disable(logging.CRITICAL)  # disable logging

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


@pytest.fixture
def runner():
    app = create_app(os.getenv('CC_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out

    db.drop_all()
    db.create_all()

    create_account_cli(app)
    create_app_cli(app)
    create_course_cli(app)
    create_event_cli(app)
    create_faker_cli(app)
    create_i18n_cli(app)

    yield app.test_cli_runner()
