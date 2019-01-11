import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from src.i18n.models import i18n_create, I18NLocale

from .models import Attribute, AttributeSchema, PersonAttribute, PersonAttributeSchema, EnumeratedValue, EnumeratedValueSchema


class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')
fake = Faker()  # Generic faker; random-locale ones don't implement everything.


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def attribute_factory(sqla):
    """Create a fake attribute."""
    attributes = sqla.query(Attribute).all()
    attribute = {
        'name_i18n': rl_fake().last_name(),
        'type_i18n': random.choice(Attribute.available_types()),
        'seq': random.randint(5, 15),
        'active': flip(),
    }

    return attribute

def enumerated_value_factory(sqla):
    """Create a fake enumerated value."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    attributes = sqla.query(Attribute).all()

    value_string = rl_fake().name()
    value_i18n = f'enumerated.{value_string}'

    locale_code = 'en-US'

    i18n_create(value_i18n, locale_code,
                value_string, description=f"Enum Value {value_string}")


    enumerated_value = {
        'attribute_id': random.choice(attributes).id,
        'value_i18n': value_i18n,
        'active': flip()
    }
    return enumerated_value


def person_attribute_enumerated_factory(sqla):
    """Create a fake person attribute that is enumerated."""
    person_attributes = sqla.query(PersonAttribute).all()
    enumerated_values = sqla.query(EnumeratedValue).all()
    current_enumerated_value = random.choice(enumerated_values)
    person_attribute = {
        'person_id': random.choice(person_attributes).id,
        'attribute_id': current_enumerated_value.attribute_id,
        'enum_value_id': current_enumerated_value.id,
        'string_value': None
    }

    return person_attribute

def person_attribute_string_factory(sqla):
    """Create a fake person attribute that is a string."""
    person_attributes = sqla.query(PersonAttribute).all()
    person_attribute = {
        'person_id': random.choice(person_attributes).id,
        'attribute_id': current_enumerated_value.attribute_id,
        'enum_value_id': None,
        'string_value': flip(),
    }

    return person_attribute





# ---- Attribute


@pytest.mark.xfail()
def test_create_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_attributes(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Enumerated_Value


@pytest.mark.xfail()
def test_create_enumerated_value(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_enumerated_values(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_enumerated_value(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_enumerated_value(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_enumerated_value(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_enumerated_value(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


# ---- Person_Attribute


@pytest.mark.xfail()
def test_create_person_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_all_person_attributes(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_read_one_person_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_replace_person_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_update_person_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False


@pytest.mark.xfail()
def test_delete_person_attribute(client, db):
    # GIVEN
    # WHEN
    # THEN
    assert True == False
