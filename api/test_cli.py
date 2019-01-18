import math
import random
import click
import os
import pytest

from src.people.models import Person, Account, Role
from src.places.models import Country
from src.i18n.models import Language, I18NLocale, I18NValue
from src import db, create_app

ccapi = __import__("cc-api")

@pytest.fixture
def init_app():
    app = create_app(os.getenv('FLASK_CONFIG') or 'test')
    app.testing = True  # Make sure exceptions percolate out

    db.drop_all()
    db.create_all()


def test_load_counties():
    init_app()
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_countries)
    assert db.session.query(Country).count() > 0


def test_load_languages():
    init_app()
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_languages)
    assert db.session.query(Language).count() > 0

def test_load_roles():
    init_app()
    assert db.session.query(Role).count() == 0
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_roles)
    assert db.session.query(Role).count() > 0

def test_load_attribute_types():
    init_app()
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_attribute_types)
    assert db.session.query(I18NValue).filter(I18NValue.key_id == 'attribute.date').count() > 0
