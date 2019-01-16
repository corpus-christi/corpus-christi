import math
import random
import click

from src.people.models import Person, Account, Role
from src.places.models import Country
from src.i18n.models import Language, I18NLocale
from src import db

ccapi = __import__("cc-api")


def test_load_counties():
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_countries)
    assert db.session.query(Country).count() > 0


def test_load_languages():
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_languages)
    assert db.session.query(Language).count() > 0


def test_load_roles():
    runner = ccapi.app.test_cli_runner()
    runner.invoke(ccapi.load_roles)
    assert db.session.query(Role).count() > 0
