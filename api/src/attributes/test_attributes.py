import pytest
import random
from .models import Attribute, AttributeSchema, Enumerated_Value, Enumerated_ValueSchema
from flask import url_for

# ---- Attribute


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def attribute_object_factory(active=1):
    """Cook up a fake attribute."""
    attribute = {
        'nameI18n': 'attribute' + str(random.randint(0, 100)),
        'typeI18n': random.choice(('Dropdown', 'Select', 'String', 'Int')),
        'seq': random.randint(0, 100),
        'active': active
    }

    return attribute


def create_multiple_attributes(sqla, n, active=1):
    """Commit `n` new attributes to the database. Return their IDs."""
    attribute_schema = AttributeSchema()
    new_attributes = []
    for i in range(n):
        valid_attribute = attribute_schema.load(
            attribute_object_factory(active))
        new_attributes.append(Attribute(**valid_attribute))
    sqla.add_all(new_attributes)
    sqla.commit()


def test_create_attribute(auth_client):
    # GIVEN an empty database
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = auth_client.post(
            url_for('attributes.create_attribute'), json=attribute_object_factory())
        assert resp.status_code == 201
    # THEN we end up with the proper number of people in the database
    assert auth_client.sqla.query(Attribute).count() == count


def test_read_all_attributes(auth_client):
    # GIVEN a DB with a collection of attributes.
    count = random.randint(3, 11)
    create_multiple_attributes(auth_client.sqla, count)

    # WHEN we ask for them all
    attributes = auth_client.sqla.query(Attribute).all()
    # THEN we exepct the same number
    assert len(attributes) == count

    # WHEN we request each of them from the server
    for attribute in attributes:
        resp = auth_client.get(
            url_for('attributes.read_one_attribute', attribute_id=attribute.id))
        # THEN we find a matching attribute
        assert resp.status_code == 200
        assert resp.json['nameI18n'] == attribute.name_i18n
        assert resp.json['typeI18n'] == attribute.type_i18n


def test_update_attribute(auth_client):
    # GIVEN a DB with an attribute.
    create_multiple_attributes(auth_client.sqla, 1)
    attribute_id = auth_client.sqla.query(Attribute.id).first().id

    # WHEN we update its fields
    payload = {}

    payload['nameI18n'] = 'updated_name'
    payload['typeI18n'] = 'updated_type'
    payload['seq'] = 0
    payload['active'] = False
    resp = auth_client.patch(url_for(
        'attributes.update_attribute', attribute_id=attribute_id), json=payload)
    assert resp.status_code == 200

    updated_attribute = auth_client.sqla.query(
        Attribute).filter_by(id=attribute_id).first()
    assert updated_attribute is not None
    assert updated_attribute.name_i18n == payload['nameI18n']
    assert updated_attribute.type_i18n == payload['typeI18n']
    assert updated_attribute.seq == payload['seq']
    assert updated_attribute.active == payload['active']


def test_deactivate_attribute(auth_client):
    # GIVEN a DB with an attribute.
    create_multiple_attributes(auth_client.sqla, 1)
    attribute_id = auth_client.sqla.query(Attribute.id).first().id

    # WHEN we call deactivate
    resp = auth_client.patch(url_for(
        'attributes.deactivate_attribute', attribute_id=attribute_id))
    assert resp.status_code == 200

    updated_attribute = auth_client.sqla.query(
        Attribute).filter_by(id=attribute_id).first()
    assert updated_attribute is not None
    assert updated_attribute.active == False


def test_activate_attribute(auth_client):
    # GIVEN a DB with an attribute.
    create_multiple_attributes(auth_client.sqla, 1, 0)
    attribute_id = auth_client.sqla.query(Attribute.id).first().id

    # WHEN we call deactivate
    resp = auth_client.patch(url_for(
        'attributes.activate_attribute', attribute_id=attribute_id))
    assert resp.status_code == 200

    updated_attribute = auth_client.sqla.query(
        Attribute).filter_by(id=attribute_id).first()
    assert updated_attribute is not None
    assert updated_attribute.active == True


# ---- Enumerated_Value

def enumerated_value_object_factory(active=1):
    """Cook up a fake enumerated value."""
    enumerated_value = {
        'valueI18n': 'enumerated_value' + str(random.randint(0, 100)),
        'active': active
    }

    return enumerated_value


def create_multiple_enumerated_values(sqla, n, active=1):
    """Commit `n` new enumerated values to the database. Return their IDs."""
    enumerated_value_schema = Enumerated_ValueSchema()
    new_enumerated_values = []
    for i in range(n):
        valid_enumerated_values = enumerated_value_schema.load(
            enumerated_value_object_factory(active))
        new_enumerated_values.append(
            Enumerated_Value(**valid_enumerated_values))
    sqla.add_all(new_enumerated_values)
    sqla.commit()


def test_create_enumerated_value(auth_client):
    # GIVEN an empty database
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = auth_client.post(
            url_for('attributes.create_enumerated_value'), json=enumerated_value_object_factory())
        assert resp.status_code == 201
    # THEN we end up with the proper number of people in the database
    assert auth_client.sqla.query(Enumerated_Value).count() == count


def test_read_all_enumerated_values(auth_client):
    # GIVEN a DB with a collection of enumerated values.
    count = random.randint(3, 11)
    create_multiple_enumerated_values(auth_client.sqla, count)

    # WHEN we ask for them all
    enumerated_values = auth_client.sqla.query(Enumerated_Value).all()
    # THEN we exepct the same number
    assert len(enumerated_values) == count

    # WHEN we request each of them from the server
    for enumerated_value in enumerated_values:
        resp = auth_client.get(
            url_for('attributes.read_one_enumerated_value', enumerated_value_id=enumerated_value.id))
        # THEN we find a matching enumerated_value
        assert resp.status_code == 200
        assert resp.json['valueI18n'] == enumerated_value.value_i18n
        assert resp.json['active'] == enumerated_value.active


def test_update_enumerated_value(auth_client):
    # GIVEN a DB with an enumerated value.
    create_multiple_enumerated_values(auth_client.sqla, 1)
    enumerated_value_id = auth_client.sqla.query(
        Enumerated_Value.id).first().id

    # WHEN we update its fields
    payload = {}

    payload['valueI18n'] = 'updated_name'
    payload['active'] = False
    resp = auth_client.patch(url_for(
        'attributes.update_enumerated_value', enumerated_value_id=enumerated_value_id), json=payload)
    assert resp.status_code == 200

    updated_enumerated_value = auth_client.sqla.query(
        Enumerated_Value).filter_by(id=enumerated_value_id).first()
    assert updated_enumerated_value is not None
    assert updated_enumerated_value.value_i18n == payload['valueI18n']
    assert updated_enumerated_value.active == payload['active']


def test_deactivate_enumerated_value(auth_client):
    # GIVEN a DB with an enumerated_value.
    create_multiple_enumerated_values(auth_client.sqla, 1)
    enumerated_value_id = auth_client.sqla.query(
        Enumerated_Value.id).first().id

    # WHEN we call deactivate
    resp = auth_client.patch(url_for(
        'attributes.deactivate_enumerated_value', enumerated_value_id=enumerated_value_id))
    assert resp.status_code == 200

    updated_enumerated_value = auth_client.sqla.query(
        Enumerated_Value).filter_by(id=enumerated_value_id).first()
    assert updated_enumerated_value is not None
    assert updated_enumerated_value.active == False


def test_activate_enumerated_value(auth_client):
    # GIVEN a DB with an enumerated_value.
    create_multiple_enumerated_values(auth_client.sqla, 1, 0)
    enumerated_value_id = auth_client.sqla.query(
        Enumerated_Value.id).first().id

    # WHEN we call deactivate
    resp = auth_client.patch(url_for(
        'attributes.activate_enumerated_value', enumerated_value_id=enumerated_value_id))
    assert resp.status_code == 200

    updated_enumerated_value = auth_client.sqla.query(
        Enumerated_Value).filter_by(id=enumerated_value_id).first()
    assert updated_enumerated_value is not None
    assert updated_enumerated_value.active == True
