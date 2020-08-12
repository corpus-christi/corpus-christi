import math
import random

import pytest
from faker import Faker
from flask import url_for
from werkzeug.security import check_password_hash

from .models import Person, PersonSchema, RoleSchema, Role
from ..i18n.models import I18NKey, i18n_create, I18NLocale
from ..images.create_image_data import create_test_images, create_images_people
from ..images.models import Image, ImagePerson
from ..groups.models import ManagerSchema


class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')
fake = Faker()  # Generic faker; random-locale ones don't implement everything.


# ---- Helper Functions

def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


# moved to above the person_object_factory
def username_factory():
    return f"{fake.pystr(min_chars=5, max_chars=15)}{fake.pyint()}"


def person_object_factory(firstName=None, lastName=None):
    """Cook up a fake person."""
    person = {
        'lastName': lastName or rl_fake().last_name(),
        'secondLastName': rl_fake().last_name(),
        'gender': random.choice(('M', 'F')),
        'username': username_factory(),
        'password': fake.password(),
        'active': flip()
    }

    # Make the person's name match their gender.
    person['firstName'] = firstName or (rl_fake().first_name_male(
    ) if person['gender'] == 'M' else rl_fake().first_name_female())
    person['active'] = True

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        person['birthday'] = rl_fake().date_of_birth(
            minimum_age=18).strftime('%Y-%m-%d')
    if flip():
        person['phone'] = rl_fake().phone_number()
    if flip():
        person['email'] = rl_fake().email()
    return person


def create_multiple_people(sqla, n, inactive=False):
    """Commit `n` new people to the database. Returns the people."""
    person_schema = PersonSchema()
    new_people = []
    for i in range(n):
        valid_person = person_schema.load(person_object_factory())
        if inactive:
            valid_person['active'] == False
        new_people.append(Person(**valid_person))
    sqla.add_all(new_people)
    sqla.commit()
    return new_people


def role_object_factory(role_name='role.test_role'):
    """Cook up a fake role."""
    role = {
        'nameI18n': role_name[:32],
        'active': 1
    }
    return role


def create_role(sqla):
    """Commit new role to the database. Return ID."""
    role_schema = RoleSchema()

    valid_role_object = role_schema.load(
        role_object_factory(
            fake.job()))  # fake role is fake job
    valid_role_row = Role(**valid_role_object)
    sqla.add(valid_role_row)
    sqla.commit()
    return valid_role_row.id


def create_roles(sqla, n):
    """Commit `n` new roles to the database. Return their IDs."""
    role_schema = RoleSchema()
    role_ids = []

    for x in range(0, n):
        role_ids.append(create_role(sqla))

    return role_ids


def create_person_roles(sqla, fraction=0.75):
    new_person_roles = []
    if not sqla.query(Person).all():
        create_multiple_people(sqla, random.randint(3, 6))
    if not sqla.query(Role).all():
        create_roles(sqla, random.randint(3, 6))
    all_persons_roles = sqla.query(Person, Role).all()
    sample_persons_roles = random.sample(
        all_persons_roles, math.floor(
            len(all_persons_roles) * fraction))
    for persons_roles in sample_persons_roles:
        persons_roles[0].roles.append(persons_roles[1])
        new_person_roles.append(persons_roles[0])
    sqla.add_all(new_person_roles)
    sqla.commit()


# ---- Person


@pytest.mark.smoke
def test_create_person(auth_client):
    # GIVEN an empty database
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = auth_client.post(url_for('people.create_person'), json={
            'person': person_object_factory(), 'attributesInfo': []})
        assert resp.status_code == 201
    # THEN we end up with the proper number of people in the database
    assert auth_client.sqla.query(Person).count() == count


@pytest.mark.smoke
def test_create_person_optional(auth_client):
    # GIVEN an empty database
    count = random.randint(3, 6)

    # GIVEN new person data
    for i in range(count):
        new_person = person_object_factory()
        flips = (flip(), flip())
        if flips[0]:
            new_person['phone'] = ""
        if flips[1] or not flips[0]:
            new_person['email'] = ""

        # WHEN the new person is requested to be created
        resp = auth_client.post(
            url_for('people.create_person'), json={
                'person': new_person, 'attributesInfo': []})

        # THEN expect the creation to run OK
        assert resp.status_code == 201

    # THEN expect people to be created
    assert auth_client.sqla.query(Person).count() == count


@pytest.mark.smoke
def test_create_person_invalid(auth_client):
    # GIVEN an empty database
    count = random.randint(3, 6)

    # GIVEN new person with bad data
    for i in range(count):
        new_person = person_object_factory()
        flips = (flip(), flip(), flip())
        if flips[0]:
            new_person['first_name'] = None
        if flips[1]:
            new_person['last_name'] = None
        if flips[2] or not (flips[0] or flips[1]):
            new_person[fake.word()] = fake.word()

        # WHEN the bad person is requested to be created
        resp = auth_client.post(
            url_for('people.create_person'), json={
                'person': new_person, 'attributesInfo': []})

        # THEN expect the creation to be unprocessable
        assert resp.status_code == 422

    # THEN expect people not to be created
    assert auth_client.sqla.query(Person).count() == 0


@pytest.mark.smoke  # not sure on this one
def test_read_all_persons(auth_client):
    # GIVEN a DB with a collection people.
    create_multiple_people(
        auth_client.sqla, random.randint(
            6, 55))  # create random people

    # WHEN the api call is made for read all persons
    resp = auth_client.get(url_for('people.read_all_persons'))
    assert resp.status_code == 200
    # THEN number of all persons returned match that of the DB
    people = auth_client.sqla.query(Person).all()
    assert len(resp.json) == len(people)


@pytest.mark.smoke
def test_read_one_person(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    people = auth_client.sqla.query(Person).all()

    # WHEN we request each of them from the server
    for person in people:
        resp = auth_client.get(
            url_for('people.read_one_person', person_id=person.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['firstName'] == person.first_name
        assert resp.json['lastName'] == person.last_name
        assert resp.json['secondLastName'] == person.second_last_name
        assert 'password' not in resp.json  # Shouldn't be exposed by API


@pytest.mark.smoke
def test_update_person(auth_client):
    # GIVEN a random person from collection of people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)
    randomId = random.randint(1, count)
    the_man = auth_client.sqla.query(Person).get(randomId)

    # WHEN we call api to update a random person's details
    new_first_name = "Really"
    new_last_name = "Big"
    new_second_last_name = "Chungus"
    update_person_json = {
        "person": {
            "active": 'true',
            'firstName': new_first_name,
            'lastName': new_last_name,
            'secondLastName': new_second_last_name,
            'gender': "M"
        },
        "attributesInfo": []
    }
    resp = auth_client.patch(
        url_for(
            'people.update_person',
            person_id=randomId),
        json=update_person_json)
    assert resp.status_code == 200

    # THEN those updates are matched with the database
    the_man = auth_client.sqla.query(Person).get(randomId)
    assert the_man.first_name == new_first_name
    assert the_man.last_name == new_last_name
    assert the_man.second_last_name == new_second_last_name


@pytest.mark.smoke
def test_update_person_invalid(auth_client):
    # GIVEN a set of people
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)

    people = auth_client.sqla.query(Person).all()

    # GIVEN bad modification data
    for person in people:
        mod = {}
        flips = (flip(), flip(), flip())
        if flips[0]:
            mod['firstName'] = None
        if flips[1]:
            mod['lastName'] = None
        if flips[2] or not (flips[0] or flips[1]):
            mod[fake.word()] = fake.word()

        # WHEN a people are updated with bad data
        resp = auth_client.patch(
            url_for(
                'people.update_person',
                person_id=person.id),
            json={
                'person': mod,
                'attributesInfo': []})

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_person_no_exist(auth_client):
    # GIVEN an empty database

    # GIVEN modification data
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

    # WHEN a person is updated with data
    resp = auth_client.patch(
        url_for(
            'people.update_person',
            person_id=random.randint(
                1,
                8)),
        json={
            'person': mod,
            'attributesInfo': []})

    # THEN expect the requested person not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_deactivate_person(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)

    # WHEN we choose a person at random
    all_people = auth_client.sqla.query(Person).all()
    current_person = random.choice(all_people)

    # WHEN we call deactivate
    resp = auth_client.put(url_for(
        'people.deactivate_person', person_id=current_person.id))
    assert resp.status_code == 200

    # THEN the person is marked as deactivated
    updated_person = auth_client.sqla.query(
        Person).filter_by(id=current_person.id).first()
    assert updated_person is not None
    assert updated_person.active == False
    return current_person.id


@pytest.mark.smoke
def test_activate_person(auth_client):
    # GIVEN a set of inactive people
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count, True)

    people = auth_client.sqla.query(Person).all()

    # WHEN each person is requested to be activated
    for person in people:
        resp = auth_client.put(
            url_for(
                'people.activate_person',
                person_id=person.id))

        # THEN expect the request to run OK
        resp.status_code == 200

    # THEN expect all inactive people to be active
    assert auth_client.sqla.query(Person).filter(
        Person.active).count() == count


@pytest.mark.smoke
def test_activate_person_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a person is requested to be activated
    resp = auth_client.put(
        url_for(
            'people.activate_person',
            person_id=random.randint(
                1,
                8)))
    # THEN expect requested person to not exist
    assert resp.status_code == 404


@pytest.mark.smoke
def test_read_one_person_by_username(auth_client):
    # GIVEN some persons
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    persons = auth_client.sqla.query(Person).all()
    # WHEN searched for by username
    person = random.choice(persons)
    resp = auth_client.get(
        url_for(
            'people.read_one_person_by_username',
            username=person.username))
    assert resp.status_code == 200  # check response
    # THEN the api response matches the database person
    assert person.id == resp.json['id']  # check db id vs api id

    # GIVEN an person name that doesn't exist in the database
    impossible_person_name = "BigChungus&UgandianKnuckles4Lyfe"
    # WHEN the api call is made for the non-existent username
    resp = auth_client.get(
        url_for(
            'people.read_one_person_by_username',
            username=impossible_person_name))
    assert resp.status_code == 404  # check response


def test_get_persons_by_role(auth_client):
    # GIVEN some persons and some roles
    create_roles(auth_client.sqla, random.randint(3, 6))
    create_multiple_people(auth_client.sqla, random.randint(3, 6))
    roles = auth_client.sqla.query(Role).all()
    persons = auth_client.sqla.query(Person).all()

    for person in persons:
        # assign roles to persons
        person.roles.append(roles[random.randint(0, len(roles) - 1)])
        auth_client.sqla.add(person)
    auth_client.sqla.commit()

    for role in roles:  # Iterate through roles and use api to compare to db
        # WHEN the api call for getting persons by role is called
        resp = auth_client.get(
            url_for(
                'people.get_persons_by_role',
                role_id=role.id))
        assert resp.status_code == 200  # check response

        person_count = 0
        for person in persons:  # count the persons that have this specific role
            if role in person.roles:
                person_count += 1
        # THEN the number of persons returned by role matches the DB
        # person_count is equal to number of entries in get_person_by_role
        assert person_count == len(resp.json)


@pytest.mark.smoke
def test_update_person(auth_client):
    # GIVEN a set of people
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)

    persons = auth_client.sqla.query(Person).all()

    for person in persons:
        mod = person_object_factory()

        # WHEN the person is requested to be updated
        resp = auth_client.patch(url_for('people.update_person',
                                         person_id=person.id),
                                 json={'person': mod, 'attributesInfo': []})

        # THEN expect the update to run OK
        assert resp.status_code == 200
        # THEN expect the person to be updated
        new_person = auth_client.sqla.query()


@pytest.mark.smoke
def test_update_person_invalid(auth_client):
    # GIVEN a set of people and roles
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_roles(auth_client.sqla, count)

    persons = auth_client.sqla.query(Person).all()
    roles = auth_client.sqla.query(Role).all()

    # GIVEN bad modification data
    for person in persons:
        mod = {}
        flips = (flip(), flip())
        if flips[0]:
            mod['username'] = None
        if flips[1] or not flips[0]:
            mod[fake.word()] = fake.word()

        # WHEN person is requested to be updated with bad data
        resp = auth_client.patch(
            url_for('people.update_person', person_id=person.id),
            json={'person': mod, 'attributesInfo': []})

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_person_no_exist(auth_client):
    # GIVEN a empty database

    # GIVEN modification data
    new_person = person_object_factory()
    mod = {}
    flips = (flip(), flip())
    if flips[0]:
        mod['username'] = new_person['username']
    if flips[1] or not flips[0]:
        mod['password'] = new_person['password']

    # WHEN a row is requested to be updated with the data
    resp = auth_client.patch(
        url_for('people.update_person', person_id=random.randint(1, 8)),
        json={'person': mod, 'attributesInfo': []})

    # THEN expect the requested person to not be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_deactivate_person(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)

    # WHEN we choose a person at random
    all_persons = auth_client.sqla.query(Person).all()
    current_person = random.choice(all_persons)

    # GIVEN a DB with an enumerated_value.

    # WHEN we call deactivate
    resp = auth_client.put(url_for(
        'people.deactivate_person', person_id=current_person.id))
    assert resp.status_code == 200

    updated_person = auth_client.sqla.query(
        Person).filter_by(id=current_person.id).first()
    assert updated_person is not None
    assert updated_person.active == False
    return current_person.id


def test_activate_person(auth_client):
    # GIVEN a DB with a collection people and persons.
    current_person_id = test_deactivate_person(auth_client)

    # WHEN we choose an person who has been deactivated
    resp = auth_client.put(url_for(
        'people.activate_person', person_id=current_person_id))
    assert resp.status_code == 200

    # THEN they are reactivated
    updated_person = auth_client.sqla.query(
        Person).filter_by(id=current_person_id).first()
    assert updated_person is not None
    assert updated_person.active


#   -----   Roles


@pytest.mark.smoke
def test_create_role(auth_client):
    # GIVEN an empty database
    count = random.randint(3, 8)
    # WHEN we create a random number of new roles
    for i in range(count):
        resp = auth_client.post(
            url_for('people.create_role'),
            json=role_object_factory(
                fake.job()))
        assert resp.status_code == 201
    # THEN we end up with the proper number of roles in the database
    assert auth_client.sqla.query(Role).count() == count


@pytest.mark.smoke
def test_create_role_invalid(auth_client):
    # GIVEN an empty database
    count = random.randint(3, 6)

    # GIVEN new roles with bad data
    for i in range(count):
        new_role = role_object_factory(fake.job())
        new_role[fake.word()] = fake.word()

        # WHEN the bad role is requested to be created
        resp = auth_client.post(url_for('people.create_role'), json=new_role)

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_read_all_roles(auth_client):
    # GIVEN a collection of roles
    role_count = random.randint(3, 8)
    create_roles(auth_client.sqla, role_count)

    # WHEN we request all roles from the api
    resp = auth_client.get(url_for('people.read_all_roles', locale='en-US'))

    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == role_count


@pytest.mark.smoke
def test_get_roles_for_person(auth_client):
    # GIVEN a set of people, roles and people-role relationships
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    #create_multiple_persons(auth_client.sqla, 1)
    create_roles(auth_client.sqla, count)
    create_person_roles(auth_client.sqla)

    persons = auth_client.sqla.query(Person).all()

    # WHEN the roles for each person are requested
    for person in persons:
        resp = auth_client.get(
            url_for(
                'people.get_roles_for_person',
                person_id=person.id))

        # THEN expect the request to run OK
        assert resp.status_code == 200

        # THEN expect the right roles to be returned for the person
        for i in range(len(person.roles)):
            assert resp.json[i] == person.roles[i].name_i18n


@pytest.mark.smoke
def test_get_roles_for_person_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN the roles for an person that does not exist are requested
    resp = auth_client.get(
        url_for(
            'people.get_roles_for_person',
            person_id=random.randint(
                1,
                8)))

    # THEN expect the requested person to not be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_read_one_role(auth_client):
    # GIVEN a set roles
    count = random.randint(3, 6)
    create_roles(auth_client.sqla, count)

    roles = auth_client.sqla.query(Role).all()

    # WHEN each role is read
    for role in roles:
        resp = auth_client.get(
            url_for(
                'people.read_one_role',
                role_id=role.id))

        # THEN expect the request to run OK
        assert resp.status_code == 200

        # THEN expect the role to be read correctly
        assert resp.json['id'] == role.id
        assert resp.json['nameI18n'] == role.name_i18n
        assert resp.json['active'] == role.active


@pytest.mark.smoke
def test_read_one_role_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a role is requested to be read
    resp = auth_client.get(
        url_for(
            'people.read_one_role',
            role_id=random.randint(
                1,
                8)))

    # THEN expect the requested role not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_update_role(auth_client):
    # GIVEN a set of roles
    count = random.randint(3, 6)
    create_roles(auth_client.sqla, count)

    roles = auth_client.sqla.query(Role).all()

    # GIVEN modification data
    for role in roles:
        new_role = role_object_factory(fake.job())
        mod = {}
        flips = (flip(), flip())
        if flips[0]:
            mod['nameI18n'] = new_role['nameI18n']
        if flips[1]:
            mod['active'] = new_role['active']

        # WHEN roles are updated with modification data
        resp = auth_client.patch(
            url_for(
                'people.update_role',
                role_id=role.id),
            json=mod)

        # THEN expect request to run OK
        assert resp.status_code == 200

        # THEN expect row to be updated
        assert resp.json['id'] == role.id
        if flips[0] and new_role['nameI18n'] != role.name_i18n:
            assert resp.json['nameI18n'] != role.name_i18n
        else:
            assert resp.json['nameI18n'] == role.name_i18n
        if flips[1] and new_role['active'] != role.active:
            assert resp.json['active'] != role.active
        else:
            assert resp.json['active'] == role.active


@pytest.mark.smoke
def test_update_role_invalid(auth_client):
    # GIVEN a set of roles
    count = random.randint(3, 6)
    create_roles(auth_client.sqla, count)

    roles = auth_client.sqla.query(Role).all()

    for role in roles:
        # WHEN roles are updated with invalid modification data
        resp = auth_client.patch(
            url_for(
                'people.update_role',
                role_id=role.id),
            json={
                fake.word(): fake.word()})

        # THEN expect request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_role_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a role is requested to be updated
    resp = auth_client.patch(
        url_for(
            'people.update_role',
            role_id=random.randint(
                1,
                8)),
        json={
            'active': False})

    # THEN expect requested role to not be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_activate_role(auth_client):
    # GIVEN a DB with a collection roles.
    Role.load_from_file()
    all_roles = auth_client.sqla.query(Role).all()
    current_role = random.choice(all_roles)

    resp = auth_client.put(url_for(
        'people.deactivate_role', role_id=current_role.id))
    assert resp.status_code == 200
    assert current_role.active == False

    # WHEN we choose a role that has been deactivated
    resp = auth_client.put(url_for(
        'people.activate_role', role_id=current_role.id))
    assert resp.status_code == 200

    # THEN the role is marked as active
    updated_role = auth_client.sqla.query(
        Role).filter_by(id=current_role.id).first()
    assert updated_role is not None
    assert updated_role.active


@pytest.mark.smoke
def test_deactivate_role(auth_client):
    # GIVEN a DB with a collection roles.
    Role.load_from_file()
    all_roles = auth_client.sqla.query(Role).all()
    current_role = random.choice(all_roles)

    # WHEN a role is chosen at random
    resp = auth_client.put(url_for(
        'people.deactivate_role', role_id=current_role.id))
    updated_role = auth_client.sqla.query(
        Role).filter_by(id=current_role.id).first()
    assert resp.status_code == 200

    # THEN the role is marked as unactive
    assert updated_role is not None
    assert current_role.active == False


@pytest.mark.smoke
def test_add_role_to_person(auth_client):
    # GIVEN a DB populated with people and roles
    create_multiple_people(auth_client.sqla, random.randint(5, 15))
    Role.load_from_file()
    all_persons = auth_client.sqla.query(Person).all()
    current_person = random.choice(all_persons)
    all_roles = auth_client.sqla.query(Role).all()
    current_role = random.choice(all_roles)

    # WHEN person and a role are specified
    resp = auth_client.post(
        url_for(
            'people.add_role_to_person',
            person_id=current_person.id,
            role_id=current_role.id))
    assert resp.status_code == 201
    role_namei18n = auth_client.sqla.query(Person).filter(
        Person.id == current_person.id).first().roles[0].name_i18n


@pytest.mark.smoke
def test_add_role_to_person_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a role is requested to be added to an person that does not exist
    resp = auth_client.post(
        url_for(
            'people.add_role_to_person', person_id=random.randint(
                1, 8), role_id=random.randint(
                1, 8)))

    # THEN expect the request to be not found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_remove_role_from_person(auth_client):
    # GIVEN a DB populated with people and roles
    create_multiple_people(auth_client.sqla, random.randint(5, 15))
    Role.load_from_file()
    all_persons = auth_client.sqla.query(Person).all()
    current_person = random.choice(all_persons)
    all_roles = auth_client.sqla.query(Role).all()
    current_role = random.choice(all_roles)

    current_person.roles.append(current_role)
    auth_client.sqla.add(current_person)
    auth_client.sqla.commit()

    # WHEN role is removed from person
    resp = auth_client.delete(
        url_for(
            'people.remove_role_from_person',
            person_id=current_person.id,
            role_id=current_role.id))

    # THEN expect the correct status code
    assert resp.status_code == 200
    # THEN person no longer is associated with the given role
    updated_role = auth_client.sqla.query(Person).filter(
        Person.id == current_person.id).first().roles
    assert updated_role == []
    assert resp.json != updated_role

    # GIVEN the person doesn't exist
    non_existant_id = -23  # person that doesn't exist

    # WHEN we try to remove a role from an person that doesnt exist
    resp = auth_client.delete(
        url_for(
            'people.remove_role_from_person',
            person_id=non_existant_id,
            role_id=current_role.id))

    # THEN we get a "person not found" 404 error
    assert resp.status_code == 404

    # GIVEN the acocunt we are trying to remove the role does not have that role
    # WHEN we try to remove that role
    resp = auth_client.delete(
        url_for(
            'people.remove_role_from_person',
            person_id=current_person.id,
            role_id=current_role.id))

    # THEN we get a 'That person does not have that role' 404 error
    assert resp.status_code == 404


@pytest.mark.smoke
def test_delete_person(auth_client):
    # GIVEN a set of people
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)

    people = auth_client.sqla.query(Person).all()

    # WHEN the people are requested to be deleted
    for person in people:
        resp = auth_client.delete(
            url_for(
                'people.delete_person',
                person_id=person.id))

        # THEN expect the delete to run OK
        assert resp.status_code == 204

    # THEN expect all people to be deleted
    assert auth_client.sqla.query(Person).count() == 0


@pytest.mark.smoke
def test_delete_person_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a person that does not exist is requested to be deleted
    resp = auth_client.delete(
        url_for(
            'people.delete_person',
            person_id=random.randint(
                1,
                8)))

    # THEN expect the requested person to not be found
    assert resp.status_code == 404


#   -----   __repr__

@pytest.mark.smoke
def test_repr_person(auth_client):
    person = Person()
    person.__repr__()


@pytest.mark.smoke
def test_repr_person(auth_client):
    create_multiple_people(auth_client.sqla, 4)
    person = auth_client.sqla.query(Person).all()
    person[0].__repr__()


@pytest.mark.smoke
def test_repr_role(auth_client):
    role = Role()
    role.__repr__()


#   -----   Person Passwords
@pytest.mark.smoke
def test_password_person(auth_client):
    person = Person()
    try:
        person.password()
        assert False
    except BaseException:
        assert True


@pytest.mark.smoke
def test_verify_password_person(auth_client):
    create_multiple_people(auth_client.sqla, 4)
    person = auth_client.sqla.query(Person).all()
    person[0].password = "test"
    person[0].verify_password("test")


def create_person(
        sqla,
        first_name,
        last_name,
        gender,
        birthday,
        phone,
        email,
        active=True,
        address_id=None):
    person_schema = PersonSchema()
    person_payload = {
        'firstName': first_name,
        'lastName': last_name,
        'gender': gender,
        'birthday': str(birthday),
        'phone': phone,
        'email': email,
        'active': active
    }
    if address_id:
        person_payload['address_id'] = address_id
    valid_person = person_schema.load(person_payload)
    person = Person(**valid_person)
    sqla.add(person)
    sqla.commit()
    return person.id


# --- Images

@pytest.mark.smoke
def test_add_people_images(auth_client):
    # GIVEN a set of people and images
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    people = auth_client.sqla.query(Person).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN an image is requested to be tied to each person
    for i in range(count):
        print(i)
        resp = auth_client.post(
            url_for(
                'people.add_people_images',
                person_id=people[i].id,
                image_id=images[i].id))

        # THEN expect the request to run OK
        assert resp.status_code == 201

        # THEN expect the person to have a single image
        assert len(
            auth_client.sqla.query(Person).filter_by(
                id=people[i].id).first().images) == 1


@pytest.mark.smoke
def test_add_people_images_no_exist(auth_client):
    # GIVEN a set of people and images
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    people = auth_client.sqla.query(Person).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN a no existant image is requested to be tied to an person
    resp = auth_client.post(
        url_for(
            'people.add_people_images',
            person_id=1,
            image_id=len(images) + 1))

    # THEN expect the image not to be found
    assert resp.status_code == 404

    # WHEN an image is requested to be tied to a no existant person
    resp = auth_client.post(
        url_for(
            'people.add_people_images',
            person_id=count + 1,
            image_id=1))

    # THEN expect the person not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_add_people_images_already_exist(auth_client):
    # GIVEN a set of people, images, and person_image relationships
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_people(auth_client.sqla)

    person_images = auth_client.sqla.query(ImagePerson).all()

    # WHEN existing person_image relationships are requested to be created
    for person_image in person_images:
        resp = auth_client.post(
            url_for(
                'people.add_people_images',
                person_id=person_image.person_id,
                image_id=person_image.image_id))

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_person_image(auth_client):
    # GIVEN a set of people, images, and person_image relationships
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_people(auth_client.sqla)

    valid_image_person = auth_client.sqla.query(ImagePerson).first()

    print(valid_image_person.person_id)

    # WHEN the person_image relationships are requested to be deleted
    resp = auth_client.delete(
        url_for(
            'people.delete_person_image',
            person_id=valid_image_person.person_id,
            image_id=valid_image_person.image_id))

    # THEN expect the delete to run OK
    assert resp.status_code == 204


@pytest.mark.smoke
def test_delete_person_image_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a person_image relationship is requested to be deleted
    resp = auth_client.delete(
        url_for(
            'people.delete_person_image', person_id=random.randint(
                1, 8), image_id=random.randint(
                1, 8)))

    # THEN expect the requested row to not be found
    assert resp.status_code == 404
