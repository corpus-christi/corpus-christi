import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Person, PersonSchema, AccountSchema, Account


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
        'gender': random.choice(('M', 'F')),
        'active': True
    }

    # Make the person's name match their gender.
    person['firstName'] = rl_fake().first_name_male() if person['gender'] == 'M' else rl_fake().first_name_female()
    person['active'] = True;

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        person['birthday'] = rl_fake().date_of_birth(minimum_age=18).strftime('%Y-%m-%d')
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
    sample_people = random.sample(all_people, math.floor(len(all_people) * fraction))

    account_schema = AccountSchema()
    new_accounts = []
    for person in sample_people:
        valid_account = account_schema.load(account_object_factory(person.id))
        new_accounts.append(Account(**valid_account))
    sqla.add_all(new_accounts)
    sqla.commit()


# ---- Person

@pytest.mark.smoke
def test_read_person_fields(auth_client):
    # GIVEN a DB with a collection of people.
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_create_person(auth_client):
    # GIVEN an empty database
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = auth_client.post(url_for('people.create_person'), json=person_object_factory())
        assert resp.status_code == 201
    # THEN we end up with the proper number of people in the database
    assert auth_client.sqla.query(Person).count() == count


@pytest.mark.smoke
def test_read_all_persons(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

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
        resp = auth_client.get(url_for('people.read_one_person', person_id=person.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['firstName'] == person.first_name
        assert resp.json['lastName'] == person.last_name

@pytest.mark.smoke
def test_update_person(auth_client):
    # GIVEN a DB with a collection of people.
    count = random.randint(3, 11)
    create_multiple_people(auth_client.sqla, count)

    # WHEN we update a random person's details
    randomId = random.randint(1,11)

    people = auth_client.sqla.query(Person).get(randomId)
    print(type(auth_client))
    print(people.first_name)

    # THEN those updates are made
    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_deactivate_person(auth_client):
    # GIVEN a DB with a collection of people
    # WHEN we deactivate an account
    # THEN the account is marked as deactivated
    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_activate_person(auth_client):
    # TODO FINISH
    assert False


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
        new_account = auth_client.sqla.query(Account).filter_by(person_id=person.id).first()
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
def test_read_all_accounts(auth_client):
    # GIVEN a collection of accounts
    prep_database(auth_client.sqla)

    # WHEN we request all accounts with the api
    resp = auth_client.get(url_for('people.read_all_accounts'))
    assert resp.status_code == 200 # Check Response

    # THEN the number of results match the request from the database
    sqlResp = auth_client.sqla.query(Account).all()
    assert len(resp.json) == len(sqlResp)


@pytest.mark.smoke
def test_read_one_account(auth_client):
    # GIVEN a collection of accounts
    prep_database(auth_client.sqla)

    for account in auth_client.sqla.query(Account).all():
        # WHEN we request one
        resp = auth_client.get(url_for('people.read_one_account', account_id=account.id))
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
        updated_account = auth_client.sqla.query(Account).filter_by(id=account_id).first()
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
        current_account = auth_client.sqla.query(Account).filter_by(id=account_id).first()
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

        resp = auth_client.patch(url_for('people.update_account', account_id=account_id), json=payload)
        assert resp.status_code == 200

    for account_id in account_ids:
        updated_account = auth_client.sqla.query(Account).filter_by(id=account_id).first()
        assert updated_account is not None
        assert updated_account.username == expected_by_id[account_id]['username']
        assert updated_account.active == expected_by_id[account_id]['active']

@pytest.mark.smoke
def test_read_one_account_by_username(auth_client):
    # GIVEN an account from the database of accounts
    account_ids = prep_database(auth_client.sqla)
    random_id = account_ids[random.randint(0,len(account_ids)-1)] # Random account id to test
    account = auth_client.sqla.query(Account).get(random_id)
    # WHEN searched for by username
    resp = auth_client.get(url_for('people.read_one_account_by_username', username=account.username))
    assert resp.status_code == 200 # check response
    # THEN the api response matches the database account
    assert account.id == resp.json['id'] # check db id vs api id

    # GIVEN an account name that doesn't exist in the database
    impossible_account_name = "BigChungus&UgandianKnuckles4Lyfe"
    # WHEN the api call is made for the non-existent username
    resp = auth_client.get(url_for('people.read_one_account_by_username', username=impossible_account_name))
    assert resp.status_code == 200  # check response
    # THEN the api should respond with an empty json respnse
    assert resp.json == {}

@pytest.mark.smoke
def test_read_person_account(auth_client):
    # GIVEN a random person from the database
    account_ids = prep_database(auth_client.sqla)
    random_id = account_ids[random.randint(0, len(account_ids) - 1)]  # Random account id to test
    account = auth_client.sqla.query(Account).get(random_id)
    print(account) #FIXME GET A PERSON ID TO SEND TO THE READ PERSON ACCOUNT
    # WHEN the api call for reading the person account is made
    resp = auth_client.get(url_for('people.read_person_account', person_id=account.personId))
    assert resp.status_code == 200  # check response
    # THEN the details match those of the db
    print(resp.json)

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_update_account(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_deactivate_account(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_activate_account(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

# ---- Role

@pytest.mark.smoke
def test_create_role(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_read_all_roles(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_get_roles_for_account(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_read_one_role(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False


@pytest.mark.smoke
def test_replace_role(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False


@pytest.mark.smoke
def test_update_role(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False


@pytest.mark.smoke
def test_delete_role(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_add_role_to_account(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False

@pytest.mark.smoke
def test_remove_role_from_account(auth_client):
    # GIVEN
    # WHEN
    # THEN

    # TODO FINISH
    assert False
