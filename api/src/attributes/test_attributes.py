import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from src.i18n.models import i18n_create, I18NLocale, I18NKey, I18NValue
from src.people.models import Person, PersonSchema
from src.people.test_people import create_multiple_people, person_object_factory

from .. import db

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

# ---- Attribute


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def add_attribute_type(name, sqla, locale_code):
    type_i18n = f'attribute.type.{name}'

    if not sqla.query(I18NLocale).get(locale_code):
        sqla.add(I18NLocale(code=locale_code, desc='English US'))

    if not sqla.query(I18NKey).get(type_i18n):
        i18n_create(type_i18n, 'en-US',
                    name, description=f"Type {name}")


def add_i18n_code(name, sqla, locale_code, name_i18n):

    if not sqla.query(I18NLocale).get(locale_code):
        sqla.add(I18NLocale(code=locale_code, desc=''))

    try:
        i18n_create(name_i18n, locale_code,
                    name, description=f"Type {name}")
    except:
        # entry is already in value table
        pass

    return name_i18n


def attribute_factory(sqla, name, locale_code='en-US', active=1):
    """Create a fake attribute."""
    name_i18n = f'attribute.name'
    add_i18n_code(name, sqla, locale_code, name_i18n)
    attributes = sqla.query(Attribute).all()
    add_attribute_type('radio', sqla, 'en-US')
    add_attribute_type('check', sqla, 'en-US')
    add_attribute_type('dropdown', sqla, 'en-US')
    add_attribute_type('float', sqla, 'en-US')
    add_attribute_type('integer', sqla, 'en-US')
    add_attribute_type('string', sqla, 'en-US')
    add_attribute_type('date', sqla, 'en-US')

    attribute = {
        'nameI18n': name_i18n,
        'typeI18n': random.choice(Attribute.available_types()),
        'seq': random.randint(5, 15),
        'active': active
    }
    return attribute


def enumerated_value_factory(sqla):
    """Create a fake enumerated value."""
    attributes = sqla.query(Attribute).all()
    if not attributes:
        create_multiple_attributes(sqla, 5, 1)
        attributes = sqla.query(Attribute).all()
    value_string = rl_fake().name()
    value_i18n = f'enumerated.{value_string}'[:32]

    locale_code = 'en-US'
    if not sqla.query(I18NLocale).get(locale_code):
        sqla.add(I18NLocale(code=locale_code, desc='English US'))

    if not sqla.query(I18NKey).get(value_i18n):
        i18n_create(value_i18n, locale_code,
                    value_string, description=f"Enum Value {value_string}")

    enumerated_value = {
        'attributeId': random.choice(attributes).id,
        'valueI18n': value_i18n,
        'active': flip()
    }
    return enumerated_value


def person_attribute_enumerated_factory(sqla):
    """Create a fake person attribute that is enumerated."""
    create_multiple_attributes(sqla, 5, 1)
    create_multiple_enumerated_values(sqla, 10)
    people = sqla.query(Person).all()
    if not people:
        create_multiple_people(sqla, random.randint(3, 6))
        people = sqla.query(Person).all()
    current_person = random.choice(people)
    enumerated_values = sqla.query(EnumeratedValue).all()
    if not enumerated_values:
        create_multiple_enumerated_values(sqla, random.randint(3, 6))
        enumerated_values = sqla.query(EnumeratedValue).all()
    current_enumerated_value = random.choice(enumerated_values)
    person_attribute = {
        'personId': current_person.id,
        'attributeId': current_enumerated_value.attribute_id,
        'enumValueId': current_enumerated_value.id
    }
    return person_attribute


def person_attribute_string_factory(sqla):
    """Create a fake person attribute that is enumerated."""
    create_multiple_attributes(sqla, 5, 1)
    people = sqla.query(Person).all()
    if not people:
        create_multiple_people(sqla, random.randint(3, 6))
        people = sqla.query(Person).all()
    current_person = random.choice(people)
    nonenumerated_values = sqla.query(Attribute).all()
    if not nonenumerated_values:
        create_multiple_nonenumerated_values(sqla, random.randint(3, 6))
        nonenumerated_values = sqla.query(Attribute).all()
    current_nonenumerated_value = random.choice(nonenumerated_values)
    person_attribute = {
        'personId': current_person.id,
        'attributeId': current_nonenumerated_value.id,
        'stringValue': rl_fake().first_name()
    }
    return person_attribute


def create_multiple_attributes(sqla, n, active=1):
    """Commit `n` new attributes to the database. Return their IDs."""
    attribute_schema = AttributeSchema()
    new_attributes = []
    for i in range(n):
        valid_attribute = attribute_schema.load(
            attribute_factory(sqla, 'name', 'en-US'))
        new_attributes.append(Attribute(**valid_attribute))
    sqla.add_all(new_attributes)
    sqla.commit()


def create_multiple_enumerated_values(sqla, n):
    """Commit `n` new enumerated values to the database. Return their IDs."""
    enumerated_value_schema = EnumeratedValueSchema(exclude=['id'])
    new_enumerated_value = []
    for i in range(n):
        valid_enumerated_value = enumerated_value_schema.load(
            enumerated_value_factory(sqla))
        new_enumerated_value.append(EnumeratedValue(**valid_enumerated_value))
    sqla.add_all(new_enumerated_value)
    sqla.commit()


def create_multiple_person_attribute_strings(sqla, n):
    """Commit `n` new person attributes that have a string type to the database. Return their IDs."""
    person_attribute_schema = PersonAttributeSchema()
    new_person_attribute = []
    for i in range(n):
        valid_person_attribute = person_attribute_schema.load(
            person_attribute_string_factory(sqla))
        new_person_attribute.append(PersonAttribute(**valid_person_attribute))
    sqla.add_all(new_person_attribute)
    sqla.commit()


def create_multiple_person_attribute_enumerated(sqla, n):
    """Commit `n` new person attributes that have an enumerated type to the database. Return their IDs."""
    person_attribute_schema = PersonAttributeSchema()
    new_person_attribute = []
    for i in range(n):
        valid_person_attribute = person_attribute_schema.load(
            person_attribute_enumerated_factory(sqla))
        new_person_attribute.append(PersonAttribute(**valid_person_attribute))
    sqla.add_all(new_person_attribute)
    sqla.commit()


def create_multiple_people_attributes(sqla, n):
    """Commit `n` new people with attributes to the database."""
    person_schema = PersonSchema()
    attribute_schema = AttributeSchema()
    person_attribute_schema = PersonAttributeSchema()
    enumerated_value_schema = EnumeratedValueSchema()
    new_people = []
    for i in range(n):
        valid_person = person_schema.load(person_object_factory())
        new_people.append(Person(**valid_person))
    sqla.add_all(new_people)
    new_attributes = [{'nameI18n': add_i18n_code('Marital Status', sqla, 'en-US', f'attribute.married'),
                       'typeI18n': add_i18n_code('attribute.radio', sqla, 'en-US', f'attribute.radio'), 'seq': 2,
                       'active': 1},
                      {'nameI18n': add_i18n_code('Home Group Name', sqla, 'en-US', f'attribute.HomeGroupName'),
                       'typeI18n': add_i18n_code('attribute.string', sqla, 'en-US', f'attribute.string'), 'seq': 1,
                       'active': 1},
                      {'nameI18n': add_i18n_code('Baptism Date', sqla, 'en-US', f'attribute.BaptismDate'),
                       'typeI18n': add_i18n_code('attribute.date', sqla, 'en-US', f'attribute.date'), 'seq': 3,
                       'active': 1}]
    new_enumerated_values = [
        {'id': 1, 'attributeId': 1, 'valueI18n': add_i18n_code('married', sqla, 'en-US', f'personAttribute.married'),
         'active': 1},
        {'id': 2, 'attributeId': 1, 'valueI18n': add_i18n_code('single', sqla, 'en-US', f'personAttribute.single'),
         'active': 1}]

    add_i18n_code('Estado Civil', sqla, 'es-EC', f'attribute.married')
    add_i18n_code('Nombre del grupo de origen', sqla, 'es-EC', f'attribute.HomeGroupName')
    add_i18n_code('Fecha de bautismo', sqla, 'es-EC', f'attribute.BaptismDate')
    add_i18n_code('casado', sqla, 'es-EC', f'personAttribute.married')
    add_i18n_code('soltero', sqla, 'es-EC', f'personAttribute.single')

    valid_attributes = []
    for attribute in new_attributes:
        valid_attribute = attribute_schema.load(attribute)
        valid_attributes.append(Attribute(**valid_attribute))
    sqla.add_all(valid_attributes)
    sqla.commit()

    valid_enumerated_values = []
    for enumerated_value in new_enumerated_values:
        valid_enumerated_value = enumerated_value_schema.load(enumerated_value)
        valid_enumerated_values.append(EnumeratedValue(**valid_enumerated_value))
    sqla.add_all(valid_enumerated_values)
    sqla.commit()

    all_people = sqla.query(Person).all()
    if not all_people:
        create_multiple_people(sqla, random.randint(3, 6))
        all_people = sqla.query(Person).all()

    count = 1
    for i in range(n):
        # current_person = random.choice(all_people)
        # person_id = current_person.id
        new_person_attributes = [{'personId': count, 'attributeId': 1, 'enumValueId': 1},
                                 {'personId': count, 'attributeId': 2, 'stringValue': "Home Group 1"},
                                 {'personId': count, 'attributeId': 3, 'stringValue': '1-15-2019'}]

        valid_person_attributes = []
        count = count + 1
        for person_attribute in new_person_attributes:
            valid_person_attribute = person_attribute_schema.load(person_attribute)
            valid_person_attributes.append(PersonAttribute(**valid_person_attribute))
        sqla.add_all(valid_person_attributes)
        sqla.commit()

def prep_database(sqla):
    """Prepare the database with a random number of attributes, some of which are enumerated, some are string.
    Returns list of IDs of the new attributes.
    """
    create_multiple_attributes(sqla, random.randint(5, 15))
    create_multiple_enumerated_values(sqla, random.randint(5, 15))
    create_multiple_person_attribute_enumerated(sqla, random.randint(5, 15))
    create_multiple_person_attribute_strings(sqla, random.randint(5, 15))
    return [attribute.id for attribute in sqla.query(Attribute.id).all()]


# ---- Attribute

@pytest.mark.smoke
def test_create_attribute(auth_client):
    # GIVEN an empty database
    Attribute.load_types_from_file()
    count = random.randint(5, 15)
    # WHEN we create a random number of new attributes
    for i in range(count):
        resp = auth_client.post(url_for('attributes.create_attribute'), json={"attribute": attribute_factory(auth_client.sqla, 'name', 'en-US'), "enumeratedValues":[]})
        assert resp.status_code == 201
    # THEN we end up with the proper number of attributes in the database
    assert auth_client.sqla.query(Attribute).count() == count

@pytest.mark.smoke
def test_create_attribute_no_exist(auth_client):
    # GIVEN an empty database
    create_multiple_attributes(auth_client.sqla, 5)

    # WHEN a attribute is requested to be created but is sent in an incorrect format
    resp = auth_client.post(url_for('attributes.create_attribute'), json={"attribute": ['bad attribute'], "enumeratedValues":[]})

    # THEN expect the request to be not found
    assert resp.status_code == 422

@pytest.mark.smoke
def test_create_enumerated_attribute(auth_client):
    # GIVEN an empty database
    create_multiple_attributes(auth_client.sqla, 1, 1)
    count = random.randint(5, 15)
    # WHEN we create a random number of new attributes
    for i in range(count):
        resp = auth_client.post(url_for('attributes.create_attribute'),
                                json={"attribute": attribute_factory(auth_client.sqla, 'name', 'en-US'), "enumeratedValues":[enumerated_value_factory(auth_client.sqla)]})
        assert resp.status_code == 201
    # THEN we end up with the proper number of enumerated attributes in the database

    # One attribute must be created initially before creating Enumerated Values, hence the plus one below
    assert auth_client.sqla.query(Attribute).count() == count + 1
    assert auth_client.sqla.query(EnumeratedValue).count() == count


def test_read_one_attributes(auth_client):
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

@pytest.mark.slow
def test_read_all_attributes(auth_client):
    # GIVEN a DB with a collection of attributes.
    count = random.randint(3, 11)
    create_multiple_attributes(auth_client.sqla, count, 1)
    assert count > 0

    attributes = auth_client.sqla.query(Attribute).all()

    # WHEN we request all attributes from the server
    resp = auth_client.get(url_for('attributes.read_all_attributes', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == count


def test_update_attribute(auth_client):
    # GIVEN a DB with attributes and enumerated values
    create_multiple_attributes(auth_client.sqla, 10)
    attribute_id = auth_client.sqla.query(Attribute.id).first().id

    create_multiple_enumerated_values(auth_client.sqla, 5)
    enumerated_values = auth_client.sqla.query(EnumeratedValue).all()
    current_enumerated_value = random.choice(enumerated_values)
    current_enumerated_value_id = current_enumerated_value.attribute_id

    update_enumerated_value = {
        'id': current_enumerated_value.id,
        'attributeId': current_enumerated_value.attribute_id,
        'valueI18n': current_enumerated_value.value_i18n,
        'active': True
    }

    payload = {}

    payload['nameI18n'] = 'updated_name'
    payload['typeI18n'] = 'updated_type'
    payload['seq'] = 0
    payload['active'] = False

    # WHEN we update attributes with both a new enumerated value and an updated enumerated value
    for i in range(2):
        if i == 0:
            resp = auth_client.patch(url_for(
                'attributes.update_attribute', attribute_id=attribute_id), json={'attribute': payload, 'enumeratedValues': [enumerated_value_factory(auth_client.sqla)]})
            assert resp.status_code == 200
        if i == 1:
            resp = auth_client.patch(url_for(
                'attributes.update_attribute', attribute_id=current_enumerated_value_id),
                json={'attribute': payload, 'enumeratedValues': [update_enumerated_value]})

            assert resp.status_code == 200

        updated_attribute = auth_client.sqla.query(
            Attribute).filter_by(id=attribute_id).first()

        #THEN attributes are updated
        assert updated_attribute is not None
        assert updated_attribute.name_i18n == payload['nameI18n']
        assert updated_attribute.type_i18n == payload['typeI18n']
        assert updated_attribute.seq == payload['seq']
        assert updated_attribute.active == payload['active']

@pytest.mark.smoke
def test_update_attribute_no_exist(auth_client):
    # GIVEN an empty database
    create_multiple_attributes(auth_client.sqla, 5)

    # WHEN a attribute is requested to be updated and is in the incorrect format
    resp = auth_client.patch(url_for('attributes.update_attribute', attribute_id=3), json={'attribute': ['bad attribute'], 'enumeratedValues': [enumerated_value_factory(auth_client.sqla)]})

    # THEN expect the request to be not found
    assert resp.status_code == 422




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

    #THEN the attribute is deactivated
    assert updated_attribute is not None
    assert updated_attribute.active == False


def test_activate_attribute(auth_client):
    # GIVEN a DB with an attribute.
    create_multiple_attributes(auth_client.sqla, 1, 0)
    attribute_id = auth_client.sqla.query(Attribute.id).first().id

    # WHEN we call activate
    resp = auth_client.patch(url_for(
        'attributes.activate_attribute', attribute_id=attribute_id))
    assert resp.status_code == 200

    updated_attribute = auth_client.sqla.query(
        Attribute).filter_by(id=attribute_id).first()

    #THEN we have an active attribute
    assert updated_attribute is not None
    assert updated_attribute.active == True


# ---- EnumeratedValue


def create_multiple_enumerated_values(sqla, n):
    """Commit `n` new enumerated values to the database. Return their IDs."""
    create_multiple_attributes(sqla, 10)
    enumerated_value_schema = EnumeratedValueSchema(exclude=['id'])
    new_enumerated_values = []
    for i in range(n):
        valid_enumerated_values = enumerated_value_schema.load(
            enumerated_value_factory(sqla))
        new_enumerated_values.append(
            EnumeratedValue(**valid_enumerated_values))
    sqla.add_all(new_enumerated_values)
    sqla.commit()


def test_create_enumerated_value(auth_client):
    # GIVEN an empty database
    create_multiple_attributes(auth_client.sqla, 1)
    count = random.randint(5, 15)
    # WHEN we create a random number of new enumerated values
    for i in range(count):
        resp = auth_client.post(
            url_for('attributes.create_enumerated_value'), json=enumerated_value_factory(auth_client.sqla))
        assert resp.status_code == 201
    # THEN we end up with the proper number of enumerated values in the database
    assert auth_client.sqla.query(EnumeratedValue).count() == count

@pytest.mark.smoke
def test_create_enumerated_value_no_exist(auth_client):
    # GIVEN an empty database
    create_multiple_attributes(auth_client.sqla, 5)

    # WHEN an enumerated value is requested to be added and is sent in an incorrect format
    resp = auth_client.post(url_for('attributes.create_enumerated_value'), json=['bad value'])

    # THEN expect the request to be not found
    assert resp.status_code == 422


def test_read_one_enumerated_values(auth_client):
    # GIVEN a DB with a collection of enumerated values.
    create_multiple_attributes(auth_client.sqla, 10)
    count = random.randint(3, 11)
    create_multiple_enumerated_values(auth_client.sqla, count)

    # WHEN we ask for them all
    enumerated_values = auth_client.sqla.query(EnumeratedValue).all()
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


@pytest.mark.slow
def test_read_all_enumerated_values(auth_client):
    # GIVEN a DB with a collection of enumerated values.
    create_multiple_attributes(auth_client.sqla, 10)
    count = random.randint(3, 11)
    create_multiple_enumerated_values(auth_client.sqla, count)
    assert count > 0

    # WHEN we request all enumerated values from the server
    resp = auth_client.get(url_for('attributes.read_all_enumerated_values', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == count


def test_update_enumerated_value(auth_client):
    # GIVEN a DB with an enumerated value.
    create_multiple_attributes(auth_client.sqla, 10)
    count = random.randint(3, 11)
    create_multiple_enumerated_values(auth_client.sqla, count)
    enumerated_value_id = auth_client.sqla.query(
        EnumeratedValue.id).first().id

    # WHEN we update its fields
    payload = {}

    payload['valueI18n'] = 'updated_name'
    payload['active'] = False
    resp = auth_client.patch(url_for(
        'attributes.update_enumerated_value', enumerated_value_id=enumerated_value_id), json=payload)
    assert resp.status_code == 200

    updated_enumerated_value = auth_client.sqla.query(
        EnumeratedValue).filter_by(id=enumerated_value_id).first()

    #THEN we have an updated enumerated value
    assert updated_enumerated_value is not None
    assert updated_enumerated_value.value_i18n == payload['valueI18n']
    assert updated_enumerated_value.active == payload['active']

@pytest.mark.smoke
def test_update_enumerated_value_no_exist(auth_client):
    # GIVEN an empty database
    create_multiple_attributes(auth_client.sqla, 5)
    create_multiple_enumerated_values(auth_client.sqla, 5)
    enumerated_value_id = auth_client.sqla.query(
        EnumeratedValue.id).first().id

    # WHEN a enumerated value is requested to be updated and the value is in an incorrect format
    resp = auth_client.patch(url_for('attributes.update_enumerated_value', enumerated_value_id=enumerated_value_id), json=['bad attribute'])

    # THEN expect the request to be not found
    assert resp.status_code == 422


def test_deactivate_enumerated_value(auth_client):
    # GIVEN a DB with an enumerated_value.
    create_multiple_attributes(auth_client.sqla, 10)
    create_multiple_enumerated_values(auth_client.sqla, 1)
    enumerated_value_id = auth_client.sqla.query(
        EnumeratedValue.id).first().id

    # WHEN we call deactivate
    resp = auth_client.patch(url_for(
        'attributes.deactivate_enumerated_value', enumerated_value_id=enumerated_value_id))
    assert resp.status_code == 200

    updated_enumerated_value = auth_client.sqla.query(
        EnumeratedValue).filter_by(id=enumerated_value_id).first()

    # THEN the enumerated value is deactivated
    assert updated_enumerated_value is not None
    assert updated_enumerated_value.active == False


def test_activate_enumerated_value(auth_client):
    # GIVEN a DB with an enumerated_value.
    create_multiple_attributes(auth_client.sqla, 10)
    create_multiple_enumerated_values(auth_client.sqla, 1)
    enumerated_value_id = auth_client.sqla.query(
        EnumeratedValue.id).first().id

    # WHEN we call activate
    resp = auth_client.patch(url_for(
        'attributes.activate_enumerated_value', enumerated_value_id=enumerated_value_id))
    assert resp.status_code == 200

    updated_enumerated_value = auth_client.sqla.query(
        EnumeratedValue).filter_by(id=enumerated_value_id).first()

    #THEN we have an activated enumerated value
    assert updated_enumerated_value is not None
    assert updated_enumerated_value.active == True

@pytest.mark.smoke
def test_repr_attribute(auth_client):
    attribute = Attribute()
    attribute.__repr__()

@pytest.mark.smoke
def test_repr_enumerated_value(auth_client):
    enumerated_value = EnumeratedValue()
    enumerated_value.__repr__()

@pytest.mark.smoke
def test_repr_person_attribute(auth_client):
    person_attribute = PersonAttribute()
    person_attribute.__repr__()

# ---- PersonAttributes

@pytest.mark.smoke
def test_create_person_with_attributes_enumerated(auth_client):
    # GIVEN an empty database
    create_multiple_people(auth_client.sqla, 17)
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = auth_client.post(url_for('people.create_person'), json={
            'person': person_object_factory(),
            'attributesInfo': [person_attribute_enumerated_factory(auth_client.sqla)]})
        assert resp.status_code == 201
    # THEN we end up with the proper number of people attributes that are enumerated in the database
    assert auth_client.sqla.query(PersonAttribute).count() == count


@pytest.mark.smoke
def test_create_person_with_attributes_string(auth_client):
    # GIVEN an empty database
    create_multiple_people(auth_client.sqla, 17)
    count = random.randint(5, 15)
    # WHEN we create a random number of new people attributes
    for i in range(count):
        resp = auth_client.post(url_for('people.create_person'), json={
            'person': person_object_factory(), 'attributesInfo': [person_attribute_string_factory(auth_client.sqla)]})
        assert resp.status_code == 201
    # THEN we end up with the proper number of people attributes of the string type in the database
    assert auth_client.sqla.query(PersonAttribute).count() == count


def test_update_person_attributes_enumerated(auth_client):
    # GIVEN an empty database

    create_multiple_people_attributes(auth_client.sqla, 15)

    all_people = auth_client.sqla.query(Person).all()

    update_person = random.choice(all_people)
    person_attributes = auth_client.sqla.query(PersonAttribute).filter(
        PersonAttribute.person_id == update_person.id).all()

    # WHEN we update person attributes
    attribute_list = []
    for current_person_attribute in person_attributes:
        if current_person_attribute.enum_value_id == None:
            update_json = {
                'personId': update_person.id,
                'attributeId': current_person_attribute.attribute_id,
                'stringValue': 'update'
            }

        else:
            if current_person_attribute.enum_value_id == 1:
                current_person_attribute.enum_value_id = 2
            else:
                current_person_attribute.enum_value_id = 1
            update_json = {
                'personId': update_person.id,
                'attributeId': current_person_attribute.attribute_id,
                'enumValueId': current_person_attribute.enum_value_id
            }
        attribute_list.append(update_json)

    valid_person = PersonSchema().load({'firstName': 'Rita', 'lastName': 'Smith', 'gender': 'F', 'active': True})
    valid_person_attributes = PersonAttributeSchema().load(update_json)

    resp = auth_client.put(url_for('people.update_person', person_id=update_person.id), json={
        'person': {'firstName': 'Rita', 'lastName': 'Smith', 'gender': 'F', 'active': True},
        'attributesInfo': attribute_list})

    # THEN people attributes will be updated for each individual person
    assert resp.status_code == 200

    assert resp.json['id'] == update_person.id
    for i in range(len(person_attributes)):
        assert resp.json['attributesInfo'][i]['attributeId'] == person_attributes[i].attribute_id
        if person_attributes[i].enum_value_id is not None:
            assert resp.json['attributesInfo'][i]['enumValueId'] == person_attributes[i].enum_value_id
        else:
            assert resp.json['attributesInfo'][i]['stringValue'] == 'update'


@pytest.mark.smoke
def test_read_person_fields(auth_client):
    # GIVEN an empty data base

    # WHEN read_person_fields is called by the api
    resp = auth_client.get(url_for('people.read_person_fields'))
    assert resp.status_code == 200

    # THEN the person field structure is returned
    assert resp.json['person'][0]['id'] == 'INTEGER'
    assert resp.json['person'][1]['first_name'] == 'VARCHAR(64)'
    assert resp.json['person'][2]['last_name'] == 'VARCHAR(64)'
    assert resp.json['person'][3]['second_last_name'] == 'VARCHAR(64)'
    assert resp.json['person'][4]['gender'] == 'VARCHAR(1)'
    assert resp.json['person'][5]['birthday'] == 'DATE'
    assert resp.json['person'][6]['phone'] == 'VARCHAR(64)'
    assert resp.json['person'][7]['email'] == 'VARCHAR(64)'
    assert resp.json['person'][8]['active'] == 'BOOLEAN'
    assert resp.json['person'][9]['location_id'] == 'INTEGER'
    assert resp.json['person_attributes'] == []

    # GIVEN a DB with actual attributes
    create_multiple_people(auth_client.sqla, 15)
    create_multiple_people_attributes(auth_client.sqla, 15)

    # WHEN we use the api to call the read person fields
    resp = auth_client.get(url_for('people.read_person_fields'))

    # THEN we get the correct attributes
    assert resp.json['person_attributes'] != []


@pytest.mark.smoke
def test_update_person_add_attribute(auth_client):
    # GIVEN a set of attributes and people
    count = random.randint(3, 6)
    create_multiple_attributes(auth_client.sqla, count)
    create_multiple_people(auth_client.sqla, count)

    people = auth_client.sqla.query(Person).all()

    # GIVEN modification data
    for person in people:
        new_person = person_object_factory()
        mod = {}
        flips = (flip(), flip(), flip(), flip(), flip(), flip(), flip(), flip())
        if flips[0]:
            mod['firstName'] = new_person['firstName']
        if flips[1]:
            mod['lastName'] = new_person['lastName']
        if flips[2]:
            mod['secondLastName'] = new_person['secondLastName']
        if flips[3]:
            mod['gender'] = new_person['gender']
        if flips[4]:
            mod['active'] = new_person['active']
        if flips[5] and 'birthday' in new_person.keys():
            mod['birthday'] = new_person['birthday']
        if flips[6] and 'phone' in new_person.keys():
            mod['phone'] = new_person['phone']
        if flips[7] and 'email' in new_person.keys():
            mod['email'] = new_person['email']

        # WHEN a people are updated with data and an attribute
        resp = auth_client.put(url_for('people.update_person', person_id=person.id), json={'person': mod,
                                                                                           'attributesInfo': [
                                                                                               person_attribute_string_factory(
                                                                                                   auth_client.sqla)]})

        # THEN expect the update to run OK
        assert resp.status_code == 200

        # THEN expect the person to be updated and have an attribute
        assert resp.json['id'] == person.id
        if 'firstName' in mod.keys() and mod['firstName'] != person.first_name:
            resp.json['firstName'] != person.first_name
        else:
            resp.json['firstName'] == person.first_name
        if 'lastName' in mod.keys() and mod['lastName'] != person.last_name:
            resp.json['lastName'] != person.last_name
        else:
            resp.json['lastName'] == person.last_name
        if 'secondLastName' in mod.keys() and mod['secondLastName'] != person.second_last_name:
            resp.json['secondLastName'] != person.second_last_name
        else:
            resp.json['secondLastName'] == person.second_last_name
        if 'gender' in mod.keys() and mod['gender'] != person.gender:
            resp.json['gender'] != person.gender
        else:
            resp.json['gender'] == person.gender
        if 'active' in mod.keys() and mod['active'] != person.active:
            resp.json['active'] != person.active
        else:
            resp.json['active'] == person.active
        if 'birthday' in mod.keys() and mod['birthday'] != person.birthday:
            resp.json['birthday'] != person.birthday
        else:
            resp.json['birthday'] == person.birthday
        if 'phone' in mod.keys() and mod['phone'] != person.phone:
            resp.json['phone'] != person.phone
        else:
            resp.json['phone'] == person.phone
        if 'email' in mod.keys() and mod['email'] != person.email:
            resp.json['email'] != person.email
        else:
            resp.json['email'] == person.email

        assert len(resp.json['attributesInfo']) == 1


