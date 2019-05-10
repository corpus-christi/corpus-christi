import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask.json import jsonify
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Person, PersonSchema, AccountSchema, Account, RoleSchema, Role, Manager, ManagerSchema
from ..i18n.models import I18NKey, i18n_create, I18NLocale
from ..attributes.models import Attribute, PersonAttribute, EnumeratedValue, PersonAttributeSchema, AttributeSchema, \
    EnumeratedValueSchema
from ..images.models import Image, ImageSchema, ImagePerson, ImagePersonSchema
from ..images.create_image_data import create_test_images, create_images_people


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


def person_object_factory():
    """Cook up a fake person."""
    person = {
        'lastName': rl_fake().last_name(),
        'secondLastName': rl_fake().last_name(),
        'gender': random.choice(('M', 'F')),
        'active': flip()
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


def create_multiple_accounts(sqla, fraction=0.75):
    """Commit accounts for `fraction` of `people` in DB."""
    if fraction < 0.1 or fraction > 1.0:
        raise RuntimeError(f"Fraction ({fraction}) is out of bounds")

    all_people = sqla.query(Person).all()
    if not all_people:
        create_multiple_people(sqla, random.randint(5, 10))
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


def prep_database(sqla):
    """Prepare the database with a random number of people, some of which have accounts.
    Returns list of IDs of the new accounts.
    """
    create_multiple_people(sqla, random.randint(5, 15))
    create_multiple_accounts(sqla)
    return [account.id for account in sqla.query(Account.id).all()]


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

    valid_role_object = role_schema.load(role_object_factory(fake.job()))  # fake role is fake job
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


def create_accounts_roles(sqla, fraction=0.75):
    new_accounts_roles = []
    if not sqla.query(Account).all():
        create_multiple_accounts(sqla)
    if not sqla.query(Role).all():
        create_roles(sqla, random.randint(3, 6))
    all_accounts_roles = sqla.query(Account, Role).all()
    sample_accounts_roles = random.sample(all_accounts_roles, math.floor(len(all_accounts_roles) * fraction))
    for accounts_roles in sample_accounts_roles:
        accounts_roles[0].roles.append(accounts_roles[1])
        new_accounts_roles.append(accounts_roles[0])
    sqla.add_all(new_accounts_roles)
    sqla.commit()


def manager_object_factory(sqla, description, next_level=None, locale_code='en-US'):
    """Cook up a fake person."""
    description_i18n = f'manager.description.{description.replace(" ", "_")}'[:32]

    if not sqla.query(I18NLocale).get(locale_code):
        sqla.add(I18NLocale(code=locale_code, desc='English US'))

    if not sqla.query(I18NKey).get(description_i18n):
        i18n_create(description_i18n, 'en-US',
                    description, description=f"Manager {description}")

    all_persons = sqla.query(Person).all()
    all_accounts = sqla.query(Account).all()
    if not all_accounts:
        create_multiple_accounts(sqla)
        all_accounts = sqla.query(Account).all()

    manager = {

        'person_id': random.choice(all_persons).id,
        'description_i18n': description_i18n
    }
    all_managers = sqla.query(Manager).all()

    if next_level is not None:
        next_level_description_i18n = f'manager.description.{next_level.replace(" ", "_")}'
        next_level_managers = sqla.query(Manager).filter(Manager.description_i18n == next_level_description_i18n).all()
        if (len(next_level_managers) > 0):
            manager['manager_id'] = random.choice(next_level_managers).id

    return manager


def create_multiple_managers(sqla, n, next_level=None):
    """Commit `n` new people to the database. Return their IDs."""
    manager_schema = ManagerSchema()
    new_managers = []
    for i in range(n):
        valid_manager = manager_schema.load(manager_object_factory(sqla, fake.sentences(nb=1)[0], next_level))
        new_managers.append(Manager(**valid_manager))
    sqla.add_all(new_managers)
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
def test_create_person_none(auth_client):
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
        resp = auth_client.post(url_for('people.create_person'), json={'person': new_person, 'attributesInfo': []})

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
        resp = auth_client.post(url_for('people.create_person'), json={'person': new_person, 'attributesInfo': []})

        # THEN expect the creation to be unprocessable
        assert resp.status_code == 422

    # THEN expect people not to be created
    assert auth_client.sqla.query(Person).count() == 0


@pytest.mark.smoke
def test_read_all_persons(auth_client):
    # GIVEN a DB with a collection people.

    role_count = random.randint(3, 7)
    create_roles(auth_client.sqla, role_count)  # Create x Roles and return their id's
    people_count = random.randint(30, 55)
    create_multiple_people(auth_client.sqla, people_count)  # create random people
    create_multiple_accounts(auth_client.sqla, 1.0)  # create accounts for all people

    roles = auth_client.sqla.query(Role).all()
    accounts = auth_client.sqla.query(Account).all()

    for account in accounts:
        account.roles.append(roles[random.randint(0, len(roles) - 1)])  # assign roles to accounts
        auth_client.sqla.add(account)
    auth_client.sqla.commit()

    # WHEN the api call is made for read all persons
    resp = auth_client.get(url_for('people.read_all_persons'))
    assert resp.status_code == 200
    # THEN number of all persons returned match that of the DB
    people = auth_client.sqla.query(Person).all()
    assert len(resp.json) == len(people)


@pytest.mark.smoke
def test_read_one_person(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)

    # WHEN we ask for them all
    people = auth_client.sqla.query(Person).all()
    # THEN we expect the same number
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
    resp = auth_client.put(url_for('people.update_person', person_id=randomId), json=update_person_json)
    assert resp.status_code == 200

    # THEN those updates are matched with the database
    the_man = auth_client.sqla.query(Person).get(randomId)
    assert the_man.first_name == new_first_name
    assert the_man.last_name == new_last_name
    assert the_man.second_last_name == new_second_last_name


@pytest.mark.slow
def test_test_boys_and_girl(auth_client):
    tim = "cool"
    will = "smart"
    sarah = "not mean"
    assert tim == "cool"
    assert will == "smart"
    assert sarah == "not mean"


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
        resp = auth_client.put(url_for('people.update_person', person_id=person.id),
                               json={'person': mod, 'attributesInfo': []})

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
    resp = auth_client.put(url_for('people.update_person', person_id=random.randint(1, 8)),
                           json={'person': mod, 'attributesInfo': []})

    # THEN expect the requested person not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_deactivate_person(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla, 1)

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
        resp = auth_client.put(url_for('people.activate_person', person_id=person.id))

        # THEN expect the request to run OK
        resp.status_code == 200

    # THEN expect all inactive people to be active
    assert auth_client.sqla.query(Person).filter(Person.active == True).count() == count


@pytest.mark.smoke
def test_activate_person_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a person is requested to be activated
    resp = auth_client.put(url_for('people.activate_person', person_id=random.randint(1, 8)))
    # THEN expect requested person to not exist
    assert resp.status_code == 404


# ---- Account

def test_create_account(auth_client):
    # GIVEN some randomly created people
    count = random.randint(8, 19)
    create_multiple_people(auth_client.sqla, count)
    create_role(auth_client.sqla)

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

    # GIVEN an invalid json object of bad things
    # WHEN we try to pass that to the api to create account
    # THEN we get an error
    nasty_account = {
        'username': username_factory(),
        'personId': "slks"
    }

    resp = auth_client.post(url_for('people.create_account'), json=nasty_account)
    assert resp.status_code == 422


@pytest.mark.smoke
def test_read_all_accounts(auth_client):
    # GIVEN a collection of accounts
    account_count = random.randint(10, 20)
    create_multiple_people(auth_client.sqla, account_count)
    create_multiple_accounts(auth_client.sqla, 1.0)

    # WHEN we request all managers from the api
    resp = auth_client.get(url_for('people.read_all_accounts', locale='en-US'))

    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == account_count


@pytest.mark.smoke
def test_read_one_account(auth_client):
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


@pytest.mark.smoke
def test_read_one_account_by_username(auth_client):
    # GIVEN an account from the database of accounts
    account_ids = prep_database(auth_client.sqla)
    random_id = account_ids[random.randint(0, len(account_ids) - 1)]  # Random account id to test
    account = auth_client.sqla.query(Account).get(random_id)
    # WHEN searched for by username
    resp = auth_client.get(url_for('people.read_one_account_by_username', username=account.username))
    assert resp.status_code == 200  # check response
    # THEN the api response matches the database account
    assert account.id == resp.json['id']  # check db id vs api id

    # GIVEN an account name that doesn't exist in the database
    impossible_account_name = "BigChungus&UgandianKnuckles4Lyfe"
    # WHEN the api call is made for the non-existent username
    resp = auth_client.get(url_for('people.read_one_account_by_username', username=impossible_account_name))
    assert resp.status_code == 404  # check response


@pytest.mark.smoke
def test_read_person_account(auth_client):
    # GIVEN an account with a person
    account_ids = prep_database(auth_client.sqla)
    random_id = account_ids[random.randint(0, len(account_ids) - 1)]  # Random account id to test
    account = auth_client.sqla.query(Account).get(random_id)

    # WHEN the api call for reading the person account is made
    resp = auth_client.get(url_for('people.read_person_account', person_id=account.person.id))
    assert resp.status_code == 200  # check response
    # THEN the details match those of the db
    account = auth_client.sqla.query(Account).get(random_id)
    assert resp.json['id'] == account.id
    assert resp.json['username'] == account.username
    assert resp.json["personId"] == account.person.id


def test_get_accounts_by_role(auth_client):
    # GIVEN an account with a role
    role_count = random.randint(3, 7)
    create_roles(auth_client.sqla, role_count)  # Create x Roles and return their id's
    people_count = random.randint(30, 55)
    create_multiple_people(auth_client.sqla, people_count)  # create random people
    create_multiple_accounts(auth_client.sqla, 1.0)  # create accounts for all people

    roles = auth_client.sqla.query(Role).all()
    accounts = auth_client.sqla.query(Account).all()

    for account in accounts:
        account.roles.append(roles[random.randint(0, len(roles) - 1)])  # assign roles to accounts
        auth_client.sqla.add(account)
    auth_client.sqla.commit()

    for role in roles:  # Iterate through roles and use api to compare to db
        # WHEN the api call for getting accounts by role is called
        resp = auth_client.get(url_for('people.get_accounts_by_role', role_id=role.id))
        assert resp.status_code == 200  # check response

        account_count = 0
        for account in accounts:  # count the accounts that have this specific role
            if role in account.roles:
                account_count += 1
        # THEN the number of accounts returned by role matches the DB
        assert account_count == len(resp.json)  # account_count is equal to number of entries in get_account_by_role


def test_update_account(auth_client):
    """Test that we can update the password"""
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
def test_update_account_add_roles(auth_client):
    # GIVEN a set of people, accounts and roles
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_roles(auth_client.sqla, count)

    accounts = auth_client.sqla.query(Account).all()
    roles = auth_client.sqla.query(Role).all()

    # GIVEN modification data with roles
    for account in accounts:
        new_account = account_object_factory(0)
        mod = {}
        flips = (flip(), flip())
        if flips[0]:
            mod['username'] = new_account['username']
        if flips[1]:
            mod['password'] = new_account['password']

        sample_roles = random.sample(roles, math.floor(len(roles) * 0.75))
        mod['roles'] = []
        for role in sample_roles:
            mod['roles'].append(role.id)

        # WHEN account is requested to be updated
        resp = auth_client.patch(url_for('people.update_account', account_id=account.id), json=mod)

        # THEN expect the update to run OK
        assert resp.status_code == 200

        # THEN expect the number of roles for the account is correct
        account_roles = auth_client.sqla.query(Account).filter_by(id=account.id).first().roles
        assert len(account_roles) == len(mod['roles'])


@pytest.mark.smoke
def test_update_account_invalid(auth_client):
    # GIVEN a set of people, accounts and roles
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_roles(auth_client.sqla, count)

    accounts = auth_client.sqla.query(Account).all()
    roles = auth_client.sqla.query(Role).all()

    # GIVEN bad modification data
    for account in accounts:
        mod = {}
        flips = (flip(), flip())
        if flips[0]:
            mod['username'] = None
        if flips[1] or not flips[0]:
            mod[fake.word()] = fake.word()

        # WHEN account is requested to be updated with bad data
        resp = auth_client.patch(url_for('people.update_account', account_id=account.id), json=mod)

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_account_no_exist(auth_client):
    # GIVEN a empty database

    # GIVEN modification data
    new_account = account_object_factory(0)
    mod = {}
    flips = (flip(), flip())
    if flips[0]:
        mod['username'] = new_account['username']
    if flips[1] or not flips[0]:
        mod['password'] = new_account['password']

    # WHEN a row is requested to be updated with the data
    resp = auth_client.patch(url_for('people.update_account', account_id=random.randint(1, 8)), json=mod)

    # THEN expect the requested account to not be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_deactivate_account(auth_client):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla)

    # WHEN we choose a person at random
    all_accounts = auth_client.sqla.query(Account).all()
    current_account = random.choice(all_accounts)

    # GIVEN a DB with an enumerated_value.

    # WHEN we call deactivate
    resp = auth_client.put(url_for(
        'people.deactivate_account', account_id=current_account.id))
    assert resp.status_code == 200

    updated_account = auth_client.sqla.query(
        Account).filter_by(id=current_account.id).first()
    assert updated_account is not None
    assert updated_account.active == False
    return current_account.id


def test_activate_account(auth_client):
    # GIVEN a DB with a collection people and accounts.
    current_account_id = test_deactivate_account(auth_client)

    # WHEN we choose an account who has been deactivated
    resp = auth_client.put(url_for(
        'people.activate_account', account_id=current_account_id))
    assert resp.status_code == 200

    # THEN they are reactivated
    updated_account = auth_client.sqla.query(
        Account).filter_by(id=current_account_id).first()
    assert updated_account is not None
    assert updated_account.active == True


#   -----   Roles


@pytest.mark.smoke
def test_create_role(auth_client):
    # GIVEN an empty database
    count = random.randint(3, 8)
    # WHEN we create a random number of new roles
    for i in range(count):
        resp = auth_client.post(url_for('people.create_role'), json=role_object_factory(fake.job()))
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
def test_get_roles_for_account(auth_client):
    # GIVEN a set of people, accounts, roles and account-role relationships
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_roles(auth_client.sqla, count)
    create_accounts_roles(auth_client.sqla)

    accounts = auth_client.sqla.query(Account).all()

    # WHEN the roles for each account are requested
    for account in accounts:
        resp = auth_client.get(url_for('people.get_roles_for_account', account_id=account.id))

        # THEN expect the request to run OK
        assert resp.status_code == 200

        # THEN expect the right roles to be returned for the account
        for i in range(len(account.roles)):
            assert resp.json[i] == account.roles[i].name_i18n


@pytest.mark.smoke
def test_get_roles_for_account_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN the roles for an account that does not exist are requested
    resp = auth_client.get(url_for('people.get_roles_for_account', account_id=random.randint(1, 8)))

    # THEN expect the requested account to not be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_read_one_role(auth_client):
    # GIVEN a set roles
    count = random.randint(3, 6)
    create_roles(auth_client.sqla, count)

    roles = auth_client.sqla.query(Role).all()

    # WHEN each role is read
    for role in roles:
        resp = auth_client.get(url_for('people.read_one_role', role_id=role.id))

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
    resp = auth_client.get(url_for('people.read_one_role', role_id=random.randint(1, 8)))

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
        resp = auth_client.patch(url_for('people.update_role', role_id=role.id), json=mod)

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
        resp = auth_client.patch(url_for('people.update_role', role_id=role.id), json={fake.word(): fake.word()})

        # THEN expect request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_update_role_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a role is requested to be updated
    resp = auth_client.patch(url_for('people.update_role', role_id=random.randint(1, 8)), json={'active': False})

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
    assert updated_role.active == True


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
def test_add_role_to_account(auth_client):
    # GIVEN a DB populated with people, accounts, and roles
    prep_database(auth_client.sqla)
    Role.load_from_file()
    all_accounts = auth_client.sqla.query(Account).all()
    current_account = random.choice(all_accounts)
    all_roles = auth_client.sqla.query(Role).all()
    current_role = random.choice(all_roles)

    # WHEN account and a role are specified
    resp = auth_client.post(url_for(
        'people.add_role_to_account', account_id=current_account.id, role_id=current_role.id))
    assert resp.status_code == 200
    role_namei18n = auth_client.sqla.query(Account).filter(Account.id == current_account.id).first().roles[0].name_i18n

    assert resp.json == [role_namei18n]


@pytest.mark.smoke
def test_add_role_to_account_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a role is requested to be added to an account that does not exist
    resp = auth_client.post(
        url_for('people.add_role_to_account', account_id=random.randint(1, 8), role_id=random.randint(1, 8)))

    # THEN expect the request to be not found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_remove_role_from_account(auth_client):
    # GIVEN a DB populated with people, accounts, and roles
    prep_database(auth_client.sqla)
    Role.load_from_file()
    all_accounts = auth_client.sqla.query(Account).all()
    current_account = random.choice(all_accounts)
    all_roles = auth_client.sqla.query(Role).all()
    current_role = random.choice(all_roles)

    # WHEN account and a role are added
    resp = auth_client.post(url_for(
        'people.add_role_to_account', account_id=current_account.id, role_id=current_role.id))
    assert resp.status_code == 200
    role_namei18n = auth_client.sqla.query(Account).filter(Account.id == current_account.id).first().roles[0].name_i18n

    assert resp.json == [role_namei18n]

    # WHEN role is removed from account
    resp = auth_client.delete(url_for(
        'people.remove_role_from_account', account_id=current_account.id, role_id=current_role.id))
    assert resp.status_code == 200

    # THEN account no longer is associated with the given role
    updated_role = auth_client.sqla.query(Account).filter(Account.id == current_account.id).first().roles
    assert updated_role == []
    assert resp.json != updated_role

    # GIVEN the account doesn't exist
    non_existant_id = -23  # account that doesn't exist

    # WHEN you try to remove a role from an account that doesnt exist
    resp = auth_client.delete(url_for(
        'people.remove_role_from_account', account_id=non_existant_id, role_id=current_role.id))

    # THEN you get a "account not found" 404 error
    assert resp.status_code == 404

    # GIVEN the acocunt you are trying to remove the role does not have that role
    # just try to remove the role we just removed
    # WHEN you try to remove that role
    resp = auth_client.delete(url_for(
        'people.remove_role_from_account', account_id=current_account.id, role_id=current_role.id))

    # THEN you get a 'That account does not have that role' 404 error
    assert resp.status_code == 404


# ---- Manager

@pytest.mark.smoke
def test_create_manager(auth_client):
    # GIVEN an empty database
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)

    # WHEN we create a random number of new managers and managers in the database
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_accounts(auth_client.sqla, 1)

    for i in range(manager_count):
        resp = auth_client.post(url_for('people.create_manager'),
                                json=manager_object_factory(auth_client.sqla, 'first level'))
        assert resp.status_code == 201

    # THEN we end up with the proper number of managers in the database
    assert auth_client.sqla.query(Manager).count() == manager_count


@pytest.mark.smoke
def test_create_manager_invalid(auth_client):
    # GIVEN a set of people and accounts
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla, 1)

    accounts = auth_client.sqla.query(Account).all()

    # GIVEN managers with bad data for each account
    for account in accounts:
        new_manager = manager_object_factory(auth_client.sqla, fake.sentences(nb=1)[0])
        new_manager[fake.word()] = fake.word()

        # WHEN a request is made to make a manager with bad data
        resp = auth_client.post(url_for('people.create_manager'), json=new_manager)

        # THEN expect request to be unprocessable
        assert resp.status_code == 422

    # THEN expect no managers to be created
    assert auth_client.sqla.query(Manager).count() == 0


@pytest.mark.smoke
def test_read_all_managers(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, manager_count)
    # WHEN we request all managers from the server
    resp = auth_client.get(url_for('people.read_all_managers', locale='en-US'))
    # THEN the count matches the number of entries in the database
    assert resp.status_code == 200
    assert len(resp.json) == manager_count


@pytest.mark.smoke
def test_read_one_manager(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, manager_count)

    # WHEN we ask for them all
    managers = auth_client.sqla.query(Manager).all()

    # THEN we expect the same number
    assert len(managers) == manager_count

    # WHEN we request each of them from the server
    for manager in managers:
        resp = auth_client.get(url_for('people.read_one_manager', manager_id=manager.id, locale='en-US'))
        # THEN we find a matching manager
        assert resp.status_code == 200
        assert resp.json['account_id'] == manager.account_id
        assert resp.json['manager_id'] == manager.manager_id
        assert resp.json['description_i18n'] == manager.description_i18n


@pytest.mark.smoke
def test_read_one_manager_invalid(auth_client):
    # GIVEN an empty database

    # WHEN a request is made to read a manager that does not exist
    resp = auth_client.get(url_for('people.read_one_manager', manager_id=random.randint(1, 8)))

    # THEN expect requested manager not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_update_manager(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, manager_count)

    managers = auth_client.sqla.query(Manager).all()
    accounts = auth_client.sqla.query(Account).all()

    update_manager = random.choice(managers)

    new_account_id = update_manager.account_id
    while new_account_id == update_manager.account_id:
        new_account_id = random.choice(accounts).id

    new_manager_id = update_manager.manager_id
    while new_manager_id == update_manager.manager_id or new_manager_id == update_manager.id:
        new_manager_id = random.choice(managers).id

    update_json = {
        'account_id': new_account_id,
        'manager_id': new_manager_id,
        'description_i18n': update_manager.description_i18n
    }

    # WHEN
    resp = auth_client.patch(url_for('people.update_manager', manager_id=update_manager.id), json=update_json)
    # THEN
    assert resp.status_code == 200
    assert resp.json['account_id'] == new_account_id
    assert resp.json['manager_id'] == new_manager_id


@pytest.mark.smoke
def test_update_manager_invalid(auth_client):
    # GIVEN a set of people, accounts, and managers
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, count)

    managers = auth_client.sqla.query(Manager).all()

    # GIVEN bad modification data
    for manager in managers:
        mod = {}
        flips = (flip(), flip(), flip())
        if flips[0]:
            mod['account_id'] = None
        if flips[1]:
            mod['description_i18n'] = None
        if flips[2] or not (flips[0] or flips[1]):
            mod[fake.word()] = fake.word()

        # WHEN a manager is requested to be updated with bad data
        resp = auth_client.patch(url_for('people.update_manager', manager_id=manager.id), json=mod)

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_manager(auth_client):
    # GIVEN a DB with a collection of managers.
    person_count = random.randint(10, 20)
    manager_count = random.randint(5, person_count)
    create_multiple_people(auth_client.sqla, person_count)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, manager_count)

    managers = auth_client.sqla.query(Manager).all()
    accounts = auth_client.sqla.query(Account).all()

    delete_manager = managers[0]
    subordinate = managers[1]

    update_json = {
        'manager_id': delete_manager.id
    }
    auth_client.patch(url_for('people.update_manager', manager_id=subordinate.id), json=update_json)

    # WHEN we delete the manager
    resp = auth_client.delete(url_for('people.delete_manager', manager_id=delete_manager.id))

    # THEN the manager and all references to that manager are deleted
    assert resp.status_code == 204
    assert auth_client.sqla.query(Manager).filter_by(id=delete_manager.id).first() == None
    assert auth_client.sqla.query(Manager).filter_by(id=subordinate.id).first().manager_id == None


@pytest.mark.smoke
def test_delete_manager_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a manager is requested to be deleted
    resp = auth_client.delete(url_for('people.delete_manager', manager_id=random.randint(1, 8)))

    # THEN expect the manager not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_delete_manager_with_subordinate(auth_client):
    # GIVEN a set of people, accounts, and managers
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count * 2)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, count * 2)

    # GIVEN half of the managers are subordinates of the others
    for i in range(1, count + 1):
        auth_client.sqla.query(Manager).filter(Manager.id == i).update({"manager_id": i + count})
        auth_client.sqla.commit()

    # WHEN superiors are requested to be deleted
    for i in range(1, count + 1):
        resp = auth_client.delete(url_for('people.delete_manager', manager_id=i + count))

        # THEN expect the delete to run OK
        assert resp.status_code == 204

        # THEN expect that superior was deleted
        assert auth_client.sqla.query(Manager).count() == count * 2 - i

        # THEN expect relationship with subordinate to be broken
        assert auth_client.sqla.query(Manager).filter(Manager.id == i).first().manager_id is None


@pytest.mark.smoke
def test_create_manager_with_superior(auth_client):
    # GIVEN a set of people, accounts, and managers
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count * 2)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, count)

    superiors = auth_client.sqla.query(Manager).all()

    # GIVEN data for subordinate managers
    for superior in superiors:
        new_manager = manager_object_factory(auth_client.sqla, fake.sentences(nb=1)[0])
        new_manager['manager_id'] = superior.id

        # WHEN subordinates are requested to be created
        resp = auth_client.post(url_for('people.create_manager'), json=new_manager)

        # THEN expect the create to run OK
        resp.status_code == 201

    # THEN expect the right number of managers to be created
    assert auth_client.sqla.query(Manager).count() == count * 2


@pytest.mark.smoke
def test_repr_manager(auth_client):
    # GIVEN a DB with a manager
    create_multiple_people(auth_client.sqla, 1)
    create_multiple_accounts(auth_client.sqla, 1)
    create_multiple_managers(auth_client.sqla, 1)
    managers = auth_client.sqla.query(Manager).all()
    managers[0].__repr__()



@pytest.mark.smoke
def test_delete_person(auth_client):
    # GIVEN a set of people
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)

    people = auth_client.sqla.query(Person).all()

    # WHEN the people are requested to be deleted
    for person in people:
        resp = auth_client.delete(url_for('people.delete_person', person_id=person.id))

        # THEN expect the delete to run OK
        assert resp.status_code == 204

    # THEN expect all people to be deleted
    assert auth_client.sqla.query(Person).count() == 0

@pytest.mark.smoke
def test_delete_person_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a person that does not exist is requested to be deleted
    resp = auth_client.delete(url_for('people.delete_person', person_id=random.randint(1, 8)))

    # THEN expect the requested person to not be found
    assert resp.status_code == 404


#   -----   __repr__

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


#   -----   _init

@pytest.mark.smoke
def test_init_person(auth_client):
    person = Person()
    person._init(auth_client.sqla)


#   -----   Account Passwords
@pytest.mark.smoke
def test_password_account(auth_client):
    account = Account()
    try:
        account.password()
    except:
        assert True


@pytest.mark.smoke
def test_verify_password_account(auth_client):
    create_multiple_people(auth_client.sqla, 4)
    create_multiple_accounts(auth_client.sqla, 1)
    account = auth_client.sqla.query(Account).all()
    account[0].password = "test"
    account[0].verify_password("test")
    
def create_person(sqla, first_name, last_name, gender, birthday, phone, email, active=True, address_id=None):
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
        resp = auth_client.post(url_for('people.add_people_images', person_id = people[i].id, image_id = images[i].id))

        # THEN expect the request to run OK
        assert resp.status_code == 201

        # THEN expect the person to have a single image
        assert len(auth_client.sqla.query(Person).filter_by(id = people[i].id).first().images) == 1


@pytest.mark.smoke
def test_add_people_images_no_exist(auth_client):
    # GIVEN a set of people and images
    count = random.randint(3, 6)
    create_multiple_people(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    people = auth_client.sqla.query(Person).all()
    images = auth_client.sqla.query(Image).all()
    
    # WHEN a no existant image is requested to be tied to an person
    resp = auth_client.post(url_for('people.add_people_images', person_id = 1, image_id = len(images) + 1))

    # THEN expect the image not to be found
    assert resp.status_code == 404

    # WHEN an image is requested to be tied to a no existant person
    resp = auth_client.post(url_for('people.add_people_images', person_id = count + 1, image_id = 1))

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
        resp = auth_client.post(url_for('people.add_people_images', person_id = person_image.person_id, image_id = person_image.image_id))

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
    resp = auth_client.delete(url_for('people.delete_person_image', person_id = valid_image_person.person_id, image_id = valid_image_person.image_id))

    # THEN expect the delete to run OK
    assert resp.status_code == 204


@pytest.mark.smoke
def test_delete_person_image_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN a person_image relationship is requested to be deleted
    resp = auth_client.delete(url_for('people.delete_person_image', person_id = random.randint(1, 8), image_id = random.randint(1, 8)))

    # THEN expect the requested row to not be found
    assert resp.status_code == 404


