import random

import pytest
from faker import Faker
from flask import url_for

from .models import Person, PersonSchema


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


def person_factory():
    """Cook up a fake person."""
    person = {
        'last_name': rl_fake().last_name(),
        'gender': random.choice(('M', 'F'))
    }

    # Make the person's name match their gender.
    person['first_name'] = rl_fake().first_name_male() if person['gender'] == 'M' else rl_fake().first_name_female()

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        person['birthday'] = rl_fake().date_of_birth(minimum_age=18).strftime('%Y-%m-%d')
    if flip():
        person['phone'] = rl_fake().phone_number()
    if flip():
        person['email'] = rl_fake().email()

    return person


def create_multiple_people(db, n):
    """Commit `n` new people to the database; return their records to the caller."""
    person_schema = PersonSchema()
    new_people = []
    for i in range(n):
        valid_person = person_schema.load(person_factory())
        new_people.append(Person(**valid_person))
    db.session.add_all(new_people)
    db.session.commit()
    return new_people


@pytest.mark.smoke
def test_create_person(client, db):
    # GIVEN an empty database
    count = random.randint(5, 15)
    # WHEN we create a random number of new people
    for i in range(count):
        resp = client.post(url_for('people.create_person'), json=person_factory())
        assert resp.status_code == 201
    # THEN we end up with the proper number of people in the database
    assert db.session.query(Person).count() == count


@pytest.mark.smoke
def test_read_people(client, db):
    # GIVEN a DB with a known collection of freshly-minted fake people
    for person in create_multiple_people(db, random.randint(3, 8)):
        # WHEN we request each of them
        resp = client.get(url_for('people.read_one_person', person_id=person.id))
        # THEN we find a matching person
        assert resp.status_code == 200
        assert resp.json['first_name'] == person.first_name
        assert resp.json['last_name'] == person.last_name
