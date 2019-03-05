import pytest
import random
from faker import Faker
from flask import url_for


class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')
fake = Faker()


def email_object_factory():
    email = {
        'subject': 'Test Email',
        'body': rl_fake().sentences(nb=1)[0],
        'recipients': ['tim_ours@taylor.edu']
    }

    return email


# @pytest.mark.smoke
def test_send_email(auth_client):
    # this test is intended to fail without proper credentials

    # GIVEN nothing

    # WHEN we try to send an email
    resp = auth_client.post(url_for('emails.send_email'),
                            json=email_object_factory())

    # THEN we expect the correct code
    assert resp.status_code == 200


@pytest.mark.smoke
def test_send_email_invalid(auth_client):
    # GIVEN nothing

    # WHEN we try to send an invalid email
    email = email_object_factory()
    email[fake.word()] = fake.word()
    resp = auth_client.post(url_for('emails.send_email'), json=email)

    # THEN we expect an error code
    assert resp.status_code == 422
