import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask.json import jsonify
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Person, PersonSchema, AccountSchema, Account, Role, Manager, ManagerSchema
from ..i18n.models import I18NKey, i18n_create, I18NLocale


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


def person_object_factory():
    """Cook up a fake person."""
    person = {
        'lastName': rl_fake().last_name(),
        'secondLastName': rl_fake().last_name(),
        'gender': random.choice(('M', 'F')),
        'active': True
    }

    # Make the person's name match their gender.
    person['firstName'] = rl_fake().first_name_male(
    ) if person['gender'] == 'M' else rl_fake().first_name_female()
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


def username_factory():
    return f"{fake.pystr(min_chars=5, max_chars=15)}{fake.pyint()}"


def account_object_factory(person_id):
    """Cook up a fake account."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    account = {
        'username': username_factory(),
        'password': fake.password(),
        'personId': person_id
    }
    return account


def create_multiple_people(sqla, n):
    """Commit `n` new people to the database. Return their IDs."""
    person_schema = PersonSchema()
    new_people = []
    for i in range(n):
        valid_person = person_schema.load(person_object_factory())
        new_people.append(Person(**valid_person))
    sqla.add_all(new_people)
    sqla.commit()


def create_multiple_accounts(sqla, fraction=0.75):
    """Commit accounts for `fraction` of `people` in DB."""
    if fraction < 0.1 or fraction > 1.0:
        raise RuntimeError(f"Fraction ({fraction}) is out of bounds")

    all_people = sqla.query(Person).all()
    sample_people = random.sample(
        all_people, math.floor(len(all_people) * fraction))

    account_schema = AccountSchema()
    new_accounts = []
    for person in sample_people:
        valid_account = account_schema.load(account_object_factory(person.id))
        new_accounts.append(Account(**valid_account))
    sqla.add_all(new_accounts)
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
def test_read_person(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)

    # WHEN we ask for them all
    people = auth_client.sqla.query(Person).all()
    # THEN we exepct the same number
    assert len(people) == count

    # WHEN we request each of them from the server
    for person in people:
        resp = auth_client.get(
            url_for('people.read_one_person', person_id=person.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['firstName'] == person.first_name
        assert resp.json['lastName'] == person.last_name
        assert resp.json['secondLastName'] == person.second_last_name


# ---- Account

def test_create_account(auth_client):
    # GIVEN some randomly created people
    count = random.randint(8, 19)
    create_multiple_people(auth_client.sqla, count)

    # WHEN we retrieve them all
    people = auth_client.sqla.query(Person).all()
    # THEN we get the expected number
    assert len(people) == count

    # WHEN we create accounts for each person
    for person in people:
        account = account_object_factory(person.id)
        resp = auth_client.post(url_for('people.create_account'), json=account)
        # THEN we expect them to be created
        assert resp.status_code == 201
        # AND the account exists in the database
        new_account = auth_client.sqla.query(
            Account).filter_by(person_id=person.id).first()
        assert new_account is not None
        # And the password is properly hashed (refer to docs for generate_password_hash)
        method, salt, hash = new_account.password_hash.split('$')
        key_deriv, hash_func, iters = method.split(':')
        assert key_deriv == 'pbkdf2'
        assert hash_func == 'sha256'
        assert int(iters) >= 50000
        assert len(salt) == 8
        assert len(hash) == 64  # SHA 256 / 4 bits per hex value
    # AND we end up with the proper number of accounts.
    assert auth_client.sqla.query(Account).count() == count


def prep_database(sqla):
    """Prepare the database with a random number of people, some of which have accounts.
    Returns list of IDs of the new accounts.
    """
    create_multiple_people(sqla, random.randint(5, 15))
    create_multiple_accounts(sqla)
    return [account.id for account in sqla.query(Account.id).all()]


@pytest.mark.smoke
def test_read_account(auth_client):
    # GIVEN a collection of accounts
    prep_database(auth_client.sqla)

    for account in auth_client.sqla.query(Account).all():
        # WHEN we request one
        resp = auth_client.get(
            url_for('people.read_one_account', account_id=account.id))
        # THEN we find the matching account
        assert resp.status_code == 200
        assert resp.json['username'] == account.username
        assert 'password' not in resp.json  # Shouldn't be exposed by API
        assert resp.json['active'] == True


def test_update_password(auth_client):
    # Seed the database and fetch the IDs for the new accounts.
    account_ids = prep_database(auth_client.sqla)

    # Create different passwords for each account.
    password_by_id = {}

    # GIVEN a collection of accounts
    for account_id in account_ids:
        # WHEN we update the password via the API
        new_password = password_by_id[account_id] = fake.password()
        resp = auth_client.patch(url_for('people.update_account', account_id=account_id),
                                 json={'password': new_password})
        # THEN the update worked
        assert resp.status_code == 200
        # AND the password was not returned
        assert 'password' not in resp.json

    # GIVEN a collection of accounts
    for account_id in account_ids:
        # WHEN we retrieve account details from the database
        updated_account = auth_client.sqla.query(
            Account).filter_by(id=account_id).first()
        assert updated_account is not None
        # THEN the (account-specific) password is properly hashed
        password_hash = updated_account.password_hash
        assert check_password_hash(password_hash, password_by_id[account_id])


def test_update_other_fields(auth_client):
    """Test that we can update fields _other_ than password."""
    account_ids = prep_database(auth_client.sqla)

    # For each of the accounts, grab the current value of the "other" fields.
    expected_by_id = {}
    for account_id in account_ids:
        current_account = auth_client.sqla.query(
            Account).filter_by(id=account_id).first()
        expected_by_id[account_id] = {
            'username': current_account.username,
            'active': current_account.active
        }

    for account_id in account_ids:
        payload = {}

        if flip():
            # Randomly update the username.
            new_username = username_factory()
            expected_by_id[account_id]['username'] = new_username
            payload['username'] = new_username
        if flip():
            # Randomly update the active flag.
            new_active = flip()
            expected_by_id[account_id]['active'] = new_active
            payload['active'] = new_active

        # At this point, we'll have constructed a payload that might have zero of more
        # of the fields. This lets us test various combinations of update requests.
        # The expected_by_id dictionary stores the values we expect to see in the database,
        # whether the original value retrieve earlier or the newly updated on just
        # created.

        # It's possible that none of the fields will have been selected for update,
        # which doesn't make much sense, but we'll still test for that possibility.

        resp = auth_client.patch(
            url_for('people.update_account', account_id=account_id), json=payload)
        assert resp.status_code == 200

    for account_id in account_ids:
        updated_account = auth_client.sqla.query(
            Account).filter_by(id=account_id).first()
        assert updated_account is not None
        assert updated_account.username == expected_by_id[account_id]['username']
        assert updated_account.active == expected_by_id[account_id]['active']


@pytest.mark.smoke
def test_repr_person(auth_client):
    person = Person()
    person.__repr__()


@pytest.mark.smoke
def test_repr_account(auth_client):
    create_multiple_people(auth_client.sqla, 4)
    create_multiple_accounts(auth_client.sqla, 1)
    account = auth_client.sqla.query(Account).all()
    account[0].__repr__()


@pytest.mark.smoke
def test_repr_role(auth_client):
    role = Role()
    role.__repr__()

# ---- Manager

def manager_object_factory(sqla, description, next_level = None, locale_code='en-US'):
    """Cook up a fake person."""
    description_i18n = f'manager.description.{description.replace(" ","_")}'

    if not sqla.query(I18NLocale).get(locale_code):
        sqla.add(I18NLocale(code=locale_code, desc='English US'))

    if not sqla.query(I18NKey).get(description_i18n):
        i18n_create(description_i18n, 'en-US',
                    description, description=f"Manager {description}")

    all_people = sqla.query(Person).all()

    manager = {

        'person_id': random.choice(all_people).id,
        'description_i18n': description_i18n
    }
    all_managers = sqla.query(Manager).all()

    if next_level is not None:
        next_level_description_i18n = f'manager.description.{next_level.replace(" ","_")}'
        next_level_managers = sqla.query(Manager).filter(Manager.description_i18n==next_level_description_i18n).all()
        if (len(next_level_managers) > 0):
            manager['manager_id'] = random.choice(next_level_managers).id

    return manager


def create_multiple_managers (sqla, n, description, next_level = None):
    """Commit `n` new people to the database. Return their IDs."""
    manager_schema = ManagerSchema()
    new_managers = []
    for i in range(n):
        valid_manager = manager_schema.load(manager_object_factory(sqla, description, next_level))
        new_managers.append(Manager(**valid_manager))
    sqla.add_all(new_managers)
    sqla.commit()


@pytest.mark.smoke
def test_create_manager(auth_client):
    # GIVEN an empty databaseZ
    person_count = random.randint(10,20)
    manager_count = random.randint(5, person_count)

    # WHEN we create a random number of new managers and managers in the database
    create_multiple_people(auth_client.sqla, person_count)

    for i in range(manager_count):
        resp = auth_client.post(url_for('people.create_manager'), json=manager_object_factory(auth_client.sqla, 'first level'))
        assert resp.status_code == 201

    # THEN we end up with the proper number of managers in the database
    assert auth_client.sqla.query(Manager).count() == manager_count

@pytest.mark.slow
def test_create_manager_with_manager(auth_client):
    # GIVEN an empty databaseZ
    person_count = random.randint(10,20)
    manager_count = random.randint(5, person_count)

    # WHEN we create a random number of new managers and managers in the database
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_managers(auth_client.sqla, manager_count, 'second level')

    for i in range(manager_count):
        resp = auth_client.post(url_for('people.create_manager'), json=manager_object_factory(auth_client.sqla, 'first level', next_level='second_level'))
        assert resp.status_code == 201

    # THEN we end up with the proper number of managers in the database
    managers = auth_client.sqla.query(Manager).all()
    level1_count = 0
    level2_count = 0
    for manager in managers:
        if manager.description_i18n == 'manager.description.first_level':
            level1_count = level1_count+1
            assert manager.manager_id is not None
        else:
            level2_count = level2_count+1
            assert manager.manager_id is None

    assert level1_count == manager_count
    assert level2_count == manager_count


@pytest.mark.slow
def test_read_all_managers(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_managers(auth_client.sqla, manager_count, 'test manager')
    # WHEN we request all managers from the server
    resp = auth_client.get(url_for('people.read_all_managers', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == manager_count


@pytest.mark.slow
def test_read_one_manager(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_managers(auth_client.sqla, manager_count, 'test manager')

    # WHEN we ask for them all
    managers = auth_client.sqla.query(Manager).all()

    # THEN we expect the same number
    assert len(managers) == manager_count

    # WHEN we request each of them from the server
    for manager in managers:
        resp = auth_client.get(url_for('people.read_one_manager', manager_id=manager.id, locale='en-US'))
        # THEN we find a matching manager
        assert resp.status_code == 200
        assert resp.json['person_id'] == manager.person_id
        assert resp.json['manager_id'] == manager.manager_id
        assert resp.json['description_i18n'] == manager.description_i18n


#@pytest.mark.xfail()
#def test_replace_manager(client, db):
#    # GIVEN a DB with a collection of managers.
#    # WHEN
#    # THEN
#    assert True == False


@pytest.mark.slow
def test_update_manager(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_managers(auth_client.sqla, manager_count, 'test manager')

    managers = auth_client.sqla.query(Manager).all()
    persons = auth_client.sqla.query(Person).all()

    update_manager = random.choice(managers)

    new_person_id = update_manager.person_id
    while new_person_id == update_manager.person_id:
        new_person_id = random.choice(persons).id

    new_manager_id = update_manager.manager_id
    while new_manager_id == update_manager.manager_id or new_manager_id == update_manager.id:
        new_manager_id = random.choice(managers).id

    update_json = {
        'person_id': new_person_id,
        'manager_id': new_manager_id
    }

    # WHEN
    resp = auth_client.patch(url_for('people.update_manager', manager_id=update_manager.id), json=update_json)
    # THEN
    assert resp.status_code == 200
    assert resp.json['person_id'] == new_person_id
    assert resp.json['manager_id'] == new_manager_id


#@pytest.mark.xfail()
#def test_delete_manager(client, db):
#    # GIVEN
#    # WHEN
#    # THEN
#    assert True == False


@pytest.mark.smoke
def test_repr_manager(auth_client):
    # GIVEN a DB with a manager
    create_multiple_people(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, 1, 'test manager')
    managers = auth_client.sqla.query(Manager).all()
    managers[0].__repr__()
