import pytest
import random
import datetime
import random
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import EmailSchema
from ..events.create_event_data import flip, fake, create_multiple_events, event_object_factory, email_object_factory, create_multiple_assets, create_multiple_teams, create_events_assets, create_events_teams, create_events_persons, create_events_participants, create_teams_members, get_team_ids, asset_object_factory, team_object_factory
from ..places.test_places import create_multiple_locations, create_multiple_addresses, create_multiple_areas
from ..people.test_people import create_multiple_people

fake = Faker()

@pytest.mark.smoke
def test_send_email(auth_client):
    # this test is intended to fail without proper credentials

    # GIVEN nothing

    # WHEN we try to send an email
    resp = auth_client.post(url_for('emails.send_email'), json = email_object_factory())

    # THEN we expect the correct code
    assert resp.status_code == 200


@pytest.mark.smoke
def test_send_email_invalid(auth_client):
    # GIVEN nothing

    # WHEN we try to send an invalid email
    email = email_object_factory()
    email[fake.word()] = fake.word()
    resp = auth_client.post(url_for('emails.send_email'), json = email)

    # THEN we expect an error code
    assert resp.status_code == 422

