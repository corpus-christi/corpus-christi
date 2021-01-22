import random
import smtplib

import pytest
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
        'recipients': ['qiang_wang@taylor.edu'],
        'body': 'This is a test email',
        'managerEmail': 'qiang_wang@taylor.edu',
        'reply_to': 'qiang_wang@taylor.edu',
        'cc': [],
        'bcc': []
    }

    return email


# @pytest.mark.smoke
def test_send_email(auth_client):
    # this test is intended to fail without proper credentials

    # GIVEN nothing

    # WHEN we try to send an email
    resp = auth_client.post(url_for('emails.send_email'),
                            json=email_object_factory(),
                            )

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

def test_new_email_code(auth_client):
    resp = auth_client.post(
        url_for('emails.send_email'),
        json={
            'managerName': 'Peter Parker',
            'managerEmail': 'cc-manager@example.com',
            'subject': 'Email test',
            'body': 'This is some email for testing.',
            'recipients': ['test1@example.com', 'test2@example.com']
        })
    assert resp.status_code == 200
