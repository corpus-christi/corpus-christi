import math
import random

import pytest
from faker import Faker
from flask import url_for

from .models import Person, PersonSchema, AccountSchema, Account


class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def person_object_factory():
    """Cook up a fake person."""
    person = {
        'lastName': rl_fake().last_name(),
        'gender': random.choice(('M', 'F'))
    }

    # Make the person's name match their gender.
    person['firstName'] = rl_fake().first_name_male() if person['gender'] == 'M' else rl_fake().first_name_female()

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        person['birthday'] = rl_fake().date_of_birth(minimum_age=18).strftime('%Y-%m-%d')
    if flip():
        person['phone'] = rl_fake().phone_number()
    if flip():
        person['email'] = rl_fake().email()
    return person


def account_object_factory(person_id):
    """Cook up a fake account."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    account = {
        'username': f"{fake.pystr(min_chars=5, max_chars=15)}{fake.pyint()}",
        'password': fake.password(),
        'person_id': person_id
    }
    return account


def create_multiple_people(db, n):
    """Commit `n` new people to the database. Return their IDs."""
    person_schema = PersonSchema()
    new_people = []
    for i in range(n):
        valid_person = person_schema.load(person_object_factory())
        new_people.append(Person(**valid_person))
    db.session.add_all(new_people)
    db.session.commit()


def create_multiple_accounts(db, fraction=0.75):
    """Commit accounts for `fraction` of `people` in DB."""
    if fraction < 0.1 or fraction > 1.0:
        raise RuntimeError(f"Fraction ({fraction}) is out of bounds")

    all_people = db.session.query(Person).all()
    sample_people = random.sample(all_people, math.floor(len(all_people) * fraction))

    account_schema = AccountSchema()
    new_accounts = []
    for person in sample_people:
        valid_account = account_schema.load(account_object_factory(person.id))
        new_accounts.append(Account(**valid_account))
    db.session.add_all(new_accounts)
    db.session.commit()


# ---- Person

@pytest.mark.smoke
def test_create_person(client, db):
    # GIVEN an empty database
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = client.post(url_for('people.create_person'), json=person_object_factory())
        assert resp.status_code == 201
    # THEN we end up with the proper number of people in the database
    assert db.session.query(Person).count() == count


@pytest.mark.smoke
def test_read_person(client, db):
    # GIVEN a DB with a collection people.
    count = random.randint(3, 11)
    create_multiple_people(db, count)

    # WHEN we ask for them all
    people = db.session.query(Person).all()
    # THEN we exepct the same number
    assert len(people) == count

    # WHEN we request each of them from the server
    for person in people:
        resp = client.get(url_for('people.read_one_person', person_id=person.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['firstName'] == person.first_name
        assert resp.json['lastName'] == person.last_name


# ---- Account

def test_create_account(client, db):
    # GIVEN some randomly created people
    count = random.randint(8, 19)
    create_multiple_people(db, count)

    # WHEN we retrieve them all
    people = db.session.query(Person).all()
    # THEN we get the expected number
    assert len(people) == count

    # WHEN we create accounts for each person
    for person in people:
        account = account_object_factory(person.id)
        resp = client.post(url_for('people.create_account'), json=account)
        # THEN we expect them to be created
        assert resp.status_code == 201
    # AND we end up with the proper number of accounts.
    assert db.session.query(Account).count() == count


@pytest.mark.smoke
def test_read_account(client, db):
    # GIVEN a collection of accounts
    create_multiple_people(db, random.randint(5, 15))
    create_multiple_accounts(db)

    for account in db.session.query(Account).all():
        # WHEN we request each of them
        resp = client.get(url_for('people.read_one_account', account_id=account.id))
        # THEN we find the matching account
        assert resp.status_code == 200
        assert resp.json['username'] == account.username
        assert 'password' not in resp.json  # Shouldn't be exposed by API
        assert resp.json['active'] == True
