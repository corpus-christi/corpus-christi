import datetime
import random

import pytest
from flask import url_for

from .create_event_data import flip, fake, create_multiple_events, event_object_factory, \
    create_multiple_assets, create_multiple_teams, create_events_assets, create_events_teams, \
    create_events_persons, create_events_participants, create_event_images
from .models import Event, EventPerson, EventAsset, EventParticipant, \
    EventTeam
from ..assets.models import Asset
from ..images.create_image_data import create_test_images, create_images_events
from ..images.models import Image, ImageEvent
from ..people.models import Person
from ..people.test_people import create_multiple_people
from ..places.models import Country
from ..places.test_places import create_multiple_locations, create_multiple_addresses, create_multiple_areas
from ..teams.models import Team


# ---- Event


def generate_locations(auth_client):
    Country.load_from_file()
    create_multiple_areas(auth_client.sqla, 1)
    create_multiple_addresses(auth_client.sqla, 1)
    create_multiple_locations(auth_client.sqla, 2)


@pytest.mark.smoke
def test_create_event(auth_client):
    # GIVEN an empty database
    # WHEN we create a number of events
    count = random.randint(5, 15)
    for i in range(count):
        resp = auth_client.post(
            url_for('events.create_event'), json=event_object_factory(auth_client.sqla))
        assert resp.status_code == 201

    # THEN we expect the same number of the events in the database as we created
    assert auth_client.sqla.query(Event).count() == count


@pytest.mark.smoke
def test_create_invalid_event(auth_client):
    # GIVEN an empty database
    # WHEN we attempt to add invalid events
    count = random.randint(5, 15)

    for i in range(count):
        event = event_object_factory(auth_client.sqla)

        if flip():
            event['title'] = None
        elif flip():
            event['start'] = None
        else:
            event['end'] = None

        resp = auth_client.post(url_for('events.create_event'), json=event)

        # THEN the response should have the correct code
        assert resp.status_code == 422

    # AND the database should still be empty
    assert auth_client.sqla.query(Event).count() == 0


@pytest.mark.smoke
def test_read_all_events(auth_client):
    # GIVEN a database with some events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we read all active events
    resp = auth_client.get(url_for('events.read_all_events'))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the number of active
    # all queried events from database
    events = auth_client.sqla.query(Event).all()
    inactive = 0
    for event in events:
        if not event.active:
            inactive += 1
    # THEN we expect the database has the same number of events as we created
    assert len(events) == count
    # THEN we expect the number of active events we get from the request to be the same as the number in the database
    assert len(resp.json) == count - inactive

    # THEN we expect each active event's title to correspond to the queried event's title in the database
    j = 0  # j is the index for the response array
    for i in range(count - inactive):
        if events[i].active:
            assert resp.json[j]['title'] == events[i].title
            j += 1


@pytest.mark.smoke
def test_read_all_events_with_query(auth_client):
    # GIVEN some existing events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    for _ in range(15):
        # WHEN queried for all events matching a flag
        query_string = dict()
        if flip():
            query_string['return_group'] = 'inactive'
        else:
            query_string['return_group'] = 'both'

        if flip():
            query_string['start'] = datetime.datetime.now().strftime(
                '%Y-%m-%d')
        if flip():
            query_string['end'] = datetime.datetime.now().strftime('%Y-%m-%d')

        if flip():
            query_string['title'] = 'c'

        if flip():
            query_string['location_id'] = 1

        if flip():
            query_string['include_assets'] = 1

        if flip():
            query_string['sort'] = 'start'
        elif flip():
            query_string['sort'] = 'end'
        else:
            query_string['sort'] = 'title'

        if flip():
            query_string['sort'] += '_desc'

        # THEN the response should match those flags
        resp = auth_client.get(
            url_for('events.read_all_events'), query_string=query_string)
        assert resp.status_code == 200

        for event in resp.json:
            if 'return_group' in query_string:
                if query_string['return_group'] == 'inactive':
                    assert not event['active']
            else:
                assert event['active']

            if 'start' in query_string:
                assert datetime.datetime.strptime(event['start'][:event['start'].index(
                    'T')], '%Y-%m-%d') >= datetime.datetime.strptime(query_string['start'], '%Y-%m-%d')
            if 'end' in query_string:
                assert datetime.datetime.strptime(event['end'][:event['end'].index(
                    'T')], '%Y-%m-%d') <= datetime.datetime.strptime(query_string['end'], '%Y-%m-%d')

            if 'title' in query_string:
                assert query_string['title'].lower() in event['title'].lower()

            if 'location_id' in query_string:
                assert event['location_id'] == query_string['location_id']


@pytest.mark.smoke
def test_read_one_event(auth_client):
    # GIVEN a database with a number of events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    events = auth_client.sqla.query(Event).all()

    # WHEN we ask for the events one by one
    for event in events:
        # THEN we expect each of them to correspond to the event in the database
        resp = auth_client.get(
            url_for('events.read_one_event', event_id=event.id))
        assert resp.status_code == 200
        assert resp.json['title'] == event.title
        # Date-time comes back in a slightly different format, but information is the same.
        # assert resp.json['start'] == str(event.start)


@pytest.mark.smoke
def test_read_one_missing_event(auth_client):
    # GIVEN an empty database
    # WHEN a request for a specific event is made
    resp = auth_client.get(url_for('events.read_one_event', event_id=1))

    # THEN the response should have the appropriate error code
    assert resp.status_code == 404


@pytest.mark.smoke
def test_replace_event(auth_client):
    # GIVEN a database with a number of events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)
    # WHEN we replace one event with a predefined content
    event = auth_client.sqla.query(Event).first()
    new_event = {
        'title': fake.word(),
        'start': str(fake.future_datetime(end_date="+6h")),
        'end': str(fake.date_time_between(start_date="+6h", end_date="+1d", tzinfo=None)),
        'active': flip()
    }
    resp = auth_client.put(
        url_for('events.replace_event', event_id=event.id), json=new_event)
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the event in the database to have the same content of the predefined content
    assert resp.json['id'] == event.id
    assert resp.json['title'] == new_event['title']
    assert resp.json['active'] == new_event['active']


@pytest.mark.smoke
def test_replace_invalid_event(auth_client):
    # GIVEN a database with events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we attempt to edit an invalid event
    original_event = auth_client.sqla.query(Event).first()
    modified_event = event_object_factory(auth_client.sqla)

    if flip():
        modified_event['title'] = None
    elif flip():
        modified_event['start'] = None
    else:
        modified_event['end'] = None

    resp = auth_client.put(url_for(
        'events.replace_event', event_id=original_event.id), json=modified_event)

    # THEN the response should have the correct code
    assert resp.status_code == 422
    # AND the event should be unchanged
    new_event = auth_client.sqla.query(Event).filter(
        Event.id == original_event.id).first()
    assert new_event.title == original_event.title
    assert new_event.start == original_event.start
    assert new_event.end == original_event.end


@pytest.mark.smoke
def test_update_event(auth_client):
    # GIVEN a database with a number of events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we update one event
    event = auth_client.sqla.query(Event).first()

    payload = {}
    new_event = event_object_factory(auth_client.sqla)

    flips = (flip(), flip(), flip(), flip(), flip(), flip())

    if flips[0]:
        payload['title'] = new_event['title']
    if flips[1]:
        payload['start'] = new_event['start']
    if flips[2]:
        payload['end'] = new_event['end']
    if flips[3]:
        payload['active'] = new_event['active']
    if flips[4] and 'description' in new_event.keys():
        payload['description'] = new_event['description']
    if flips[5] and 'location_id' in new_event.keys():
        payload['location_id'] = new_event['location_id']

    resp = auth_client.patch(
        url_for('events.update_event', event_id=event.id), json=payload)

    # THEN we assume the correct status code
    assert resp.status_code == 200

    # THEN we assume the correct content in the returned object
    if flips[0]:
        assert resp.json['title'] == payload['title']
    if flips[1]:
        assert resp.json['start'] == payload['start'].replace(
            ' ', 'T') + "+00:00"
    if flips[2]:
        assert resp.json['end'] == payload['end'].replace(' ', 'T') + "+00:00"
    if flips[3]:
        assert resp.json['active'] == payload['active']
    if flips[4] and 'description' in new_event.keys():
        assert resp.json['description'] == payload['description']
    if flips[5] and 'location_id' in new_event.keys():
        assert resp.json['location'] == payload['location_id']


@pytest.mark.smoke
def test_update_invalid_event(auth_client):
    # GIVEN a database with events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we attempt to edit an invalid event
    original_event = auth_client.sqla.query(Event).first()
    modified_event = event_object_factory(auth_client.sqla)

    if flip():
        modified_event['title'] = None
    elif flip():
        modified_event['start'] = None
    else:
        modified_event['end'] = None

    resp = auth_client.patch(
        url_for('events.update_event', event_id=original_event.id), json=modified_event)

    # THEN the response should have the correct code
    assert resp.status_code == 422
    # AND the event should be unchanged
    new_event = auth_client.sqla.query(Event).filter(
        Event.id == original_event.id).first()
    assert new_event.title == original_event.title
    assert new_event.start == original_event.start
    assert new_event.end == original_event.end


@pytest.mark.smoke
def test_update_missing_event(auth_client):
    # GIVEN an empty database
    # WHEN we attempt to edit an event
    event = event_object_factory(auth_client.sqla)
    resp = auth_client.patch(
        url_for('events.update_event', event_id=1), json=event)

    # THEN the response code should be correct
    assert resp.status_code == 404


@pytest.mark.smoke
def test_delete_event(auth_client):
    # GIVEN a database with a number of events
    count = random.randint(3, 11)
    create_multiple_events(auth_client.sqla, count)

    # WHEN we deactivate a number of them
    events = auth_client.sqla.query(Event).all()

    deleted = 0
    for event in events:
        if flip() and event.active:
            resp = auth_client.delete(
                url_for('events.delete_event', event_id=event.id))
            # THEN we assume the correct status code
            assert resp.status_code == 204
            deleted += 1
        elif not event.active:
            deleted += 1
    # THEN we assume the number of active events in the database to be the correct number
    new_events = auth_client.sqla.query(Event).filter(Event.active).all()
    assert len(new_events) == count - deleted


@pytest.mark.smoke
def test_delete_invalid_event(auth_client):
    # GIVEN an empty database
    # WHEN a delete request is sent
    resp = auth_client.delete(url_for('events.delete_event', event_id=1))

    # THEN the response code should be correct
    assert resp.status_code == 404
    # AND the database should still be empty
    new_events = auth_client.sqla.query(Event).filter(Event.active).all()
    assert len(new_events) == 0


# ---- Linking tables (asset <-> event)

@pytest.mark.smoke
def test_add_asset_to_event(auth_client):
    # GIVEN a database with some events and assets
    generate_locations(auth_client)
    count_assets = random.randint(15, 20)
    count_events = random.randint(3, 5)
    create_multiple_assets(auth_client.sqla, count_assets)
    create_multiple_events(auth_client.sqla, count_events)
    # WHEN we create an asset to an event
    for _ in range(count_assets):
        test_asset_id = random.randint(1, count_assets)
        test_event_id = random.randint(1, count_events + 1)
        test_asset = auth_client.sqla.query(Asset).filter(
            Asset.id == test_asset_id).first()
        test_event = auth_client.sqla.query(Event).filter(
            Event.id == test_event_id).first()
        test_asset_events = auth_client.sqla.query(EventAsset).filter_by(
            asset_id=test_asset_id).join(Event).all()
        resp = auth_client.put(url_for(
            'events.add_asset_to_event', asset_id=test_asset_id, event_id=test_event_id))
        if not test_event or not test_asset:
            assert resp.status_code == 404
            continue
        if event_overlap(test_event, test_asset_events):
            assert resp.status_code == 422
            continue
        # THEN we expect the right status code
        assert resp.status_code == 200


def event_overlap(test_event, test_asset_events):
    for asset_event in test_asset_events:
        # test for overlap with existing events
        if test_event.start <= asset_event.event.start < test_event.end \
                or asset_event.event.start <= test_event.start < asset_event.event.end \
                or test_event.start < asset_event.event.end <= test_event.end \
                or asset_event.event.start < test_event.end <= asset_event.event.end:
            return True
    return False


@pytest.mark.smoke
def test_add_asset_to_invalid_event(auth_client):
    # GIVEN a database with some events and assets
    generate_locations(auth_client)
    create_multiple_assets(auth_client.sqla, 1)
    create_multiple_events(auth_client.sqla, 1)
    # WHEN we create an asset to an event that doesn't exist
    invalid_event_id = auth_client.sqla.query(Event.id).first()[0] + 1
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.add_asset_to_event',
                  event_id=invalid_event_id, asset_id=asset_id)
    resp = auth_client.post(url)
    # THEN we expect the right status code
    assert resp.status_code == 404
    # THEN we don't expect the entry in the database's linking table
    queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(
        EventAsset.event_id == invalid_event_id, EventAsset.asset_id == asset_id).count()
    assert queried_event_asset_count == 0


@pytest.mark.smoke
def test_add_booked_asset_to_event(auth_client):
    # GIVEN a database with some events and assets linked
    generate_locations(auth_client)
    create_multiple_assets(auth_client.sqla, 1)
    create_multiple_events(auth_client.sqla, 2)
    create_events_assets(auth_client.sqla, 1)

    event_id = auth_client.sqla.query(Event.id).first()[0]
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(
        EventAsset.event_id == event_id, EventAsset.asset_id == asset_id).count()
    # WHEN we create an asset to an event
    url = url_for('events.add_asset_to_event',
                  event_id=event_id, asset_id=asset_id)
    resp = auth_client.post(url)
    # THEN we expect the right status code
    assert resp.status_code == 422
    # THEN we expect the entry not to be duplicated in the database's linking table
    new_queried_event_asset_count = auth_client.sqla.query(EventAsset).filter(
        EventAsset.event_id == event_id, EventAsset.asset_id == asset_id).count()
    assert queried_event_asset_count == new_queried_event_asset_count


@pytest.mark.smoke
def test_remove_asset_from_event(auth_client):
    # GIVEN a database with some linked events and assets
    generate_locations(auth_client)
    create_multiple_assets(auth_client.sqla, 5)
    create_multiple_events(auth_client.sqla, 5)
    create_events_assets(auth_client.sqla, 1)
    link_count = auth_client.sqla.query(EventAsset).count()
    # WHEN we unlink an asset from an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.remove_asset_from_event',
                  event_id=event_id, asset_id=asset_id)
    resp = auth_client.delete(url)
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the number of entries in the database's linking table to be one less
    new_link_count = auth_client.sqla.query(EventAsset).count()
    assert new_link_count == link_count - 1
    # WHEN we unlink the same asset
    resp = auth_client.delete(url)
    # THEN We expect an error
    assert resp.status_code == 404


@pytest.mark.smoke
def test_remove_unbooked_asset_from_event(auth_client):
    # GIVEN a database with some linked events and assets
    generate_locations(auth_client)
    create_multiple_assets(auth_client.sqla, 5)
    create_multiple_events(auth_client.sqla, 5)
    create_events_assets(auth_client.sqla, 1)
    link_count = auth_client.sqla.query(EventAsset).count()
    # WHEN we unlink an asset from an event
    invalid_event_id = 30
    asset_id = auth_client.sqla.query(Asset.id).first()[0]
    url = url_for('events.remove_asset_from_event',
                  event_id=invalid_event_id, asset_id=asset_id)
    resp = auth_client.delete(url)
    # THEN we expect the right status code
    assert resp.status_code == 404
    # THEN we expect the number of entries in the database's linking table to be one less
    new_link_count = auth_client.sqla.query(EventAsset).count()
    assert new_link_count == link_count


# ---- Linking tables (event <-> team)

@pytest.mark.smoke
def test_add_event_team(auth_client):
    # GIVEN a database with only some teams
    create_multiple_teams(auth_client.sqla, 5)
    team_id = auth_client.sqla.query(Team.id).first()[0]
    # WHEN we try to link a non-existent event to a team
    resp = auth_client.post(
        url_for('events.add_event_team', event_id=1, team_id=team_id))
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked events and teams
    create_multiple_events(auth_client.sqla, 5)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    # WHEN we link a team with an event
    resp = auth_client.post(
        url_for('events.add_event_team', event_id=event_id, team_id=team_id))
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked event and team in the database
    count = auth_client.sqla.query(EventTeam).filter(
        EventTeam.event_id == event_id, EventTeam.team_id == team_id).count()
    assert count == 1
    # WHEN we link the same team again
    resp = auth_client.post(
        url_for('events.add_event_team', event_id=event_id, team_id=team_id))
    # THEN we expect an error status code
    assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_event_team(auth_client):
    # GIVEN a database with some linked events and teams
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_teams(auth_client.sqla, 5)
    create_events_teams(auth_client.sqla, 1)
    event_team = auth_client.sqla.query(EventTeam).first()
    count = auth_client.sqla.query(EventTeam).count()
    # WHEN we unlink an assets from an event
    resp = auth_client.delete(url_for(
        'events.delete_event_team', event_id=event_team.event_id, team_id=event_team.team_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be absent in the database
    assert 0 == auth_client.sqla.query(EventTeam).filter(
        EventTeam.event_id == event_team.event_id, EventTeam.team_id == event_team.team_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(EventTeam).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for(
        'events.delete_event_team', event_id=event_team.event_id, team_id=event_team.team_id))
    # THEN we expect an error
    assert resp.status_code == 404


# ---- Linking tables (event <-> person)


@pytest.mark.smoke
def test_add_event_persons(auth_client):
    description = fake.sentences(nb=1)[0]
    payload = {
        'description': description
    }
    # GIVEN a database with only some persons
    create_multiple_people(auth_client.sqla, 5)
    person_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existent event to a person
    resp = auth_client.post(url_for(
        'events.add_event_persons', event_id=1, person_id=person_id), json=payload)
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked events and persons
    create_multiple_events(auth_client.sqla, 5)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    # WHEN we try to make a link without description
    resp = auth_client.post(
        url_for('events.add_event_persons', event_id=1, person_id=person_id))
    # THEN we expect an error code
    assert resp.status_code == 422
    # WHEN we link a person with an event
    resp = auth_client.post(url_for(
        'events.add_event_persons', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked event and person in the database
    count = auth_client.sqla.query(EventPerson).filter(
        EventPerson.event_id == event_id, EventPerson.person_id == person_id).count()
    assert count == 1
    # WHEN we link the same person again
    resp = auth_client.post(url_for(
        'events.add_event_persons', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error status code
    assert resp.status_code == 422


@pytest.mark.smoke
def test_modify_event_person(auth_client):
    description = fake.sentences(nb=1)[0]
    payload = {
        'description': description
    }
    # GIVEN a database with unlinked events and persons
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    # WHEN we try to modify a person not associated with an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    person_id = auth_client.sqla.query(Person.id).first()[0]
    resp = auth_client.patch(url_for(
        'events.modify_event_person', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error
    assert resp.status_code == 404
    # GIVEN a database with some linked events and persons
    create_events_persons(auth_client.sqla, 1)
    event_person = auth_client.sqla.query(EventPerson).first()
    # WHEN we try to modify an event_person without a payload
    resp = auth_client.patch(url_for('events.modify_event_person',
                                     event_id=event_person.event_id, person_id=event_person.person_id))
    # THEN we expect the error code
    assert resp.status_code == 422
    # WHEN we modify an event_person
    resp = auth_client.patch(url_for('events.modify_event_person',
                                     event_id=event_person.event_id, person_id=event_person.person_id), json=payload)
    # THEN we expect the correct code
    assert resp.status_code == 200
    # THEN we expect the event_person to be modified
    queried_description = auth_client.sqla.query(EventPerson.description).filter(
        EventPerson.event_id == event_person.event_id, EventPerson.person_id == event_person.person_id).first()[0]
    assert queried_description == description


@pytest.mark.smoke
def test_delete_event_persons(auth_client):
    # GIVEN a database with some linked events and persons
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_events_persons(auth_client.sqla, 1)
    event_person = auth_client.sqla.query(EventPerson).first()
    count = auth_client.sqla.query(EventPerson).count()
    # WHEN we unlink an assets from an event
    resp = auth_client.delete(url_for('events.delete_event_persons',
                                      event_id=event_person.event_id, person_id=event_person.person_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be absent in the database
    assert 0 == auth_client.sqla.query(EventPerson).filter(
        EventPerson.event_id == event_person.event_id, EventPerson.person_id == event_person.person_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(EventPerson).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('events.delete_event_persons',
                                      event_id=event_person.event_id, person_id=event_person.person_id))
    # THEN we expect an error
    assert resp.status_code == 404


# ---- Linking tables (event <-> participant)


@pytest.mark.smoke
def test_add_event_participants(auth_client):
    payload = {
        'confirmed': flip()
    }
    # GIVEN a database with only some participants
    create_multiple_people(auth_client.sqla, 5)
    person_id = auth_client.sqla.query(Person.id).first()[0]
    # WHEN we try to link a non-existent event to a participant
    resp = auth_client.post(url_for(
        'events.add_event_participants', event_id=1, person_id=person_id), json=payload)
    # THEN we expect an error code
    assert resp.status_code == 404
    # GIVEN a database with some unlinked events and participants
    create_multiple_events(auth_client.sqla, 5)
    event_id = auth_client.sqla.query(Event.id).first()[0]
    # WHEN we try to make a link without description
    resp = auth_client.post(
        url_for('events.add_event_participants', event_id=1, person_id=person_id))
    # THEN we expect an error code
    assert resp.status_code == 422
    # WHEN we link a participant with an event
    resp = auth_client.post(url_for('events.add_event_participants',
                                    event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect the right status code
    assert resp.status_code == 200
    # THEN we expect the correct count of linked event and participant in the database
    count = auth_client.sqla.query(EventParticipant).filter(
        EventParticipant.event_id == event_id, EventParticipant.person_id == person_id).count()
    assert count == 1
    # WHEN we link the same participant again
    resp = auth_client.post(url_for('events.add_event_participants',
                                    event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error status code
    assert resp.status_code == 422


@pytest.mark.smoke
def test_modify_event_participant(auth_client):
    payload = {
        'confirmed': flip()
    }
    # GIVEN a database with unlinked events and participants
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    # WHEN we try to modify a participant not associated with an event
    event_id = auth_client.sqla.query(Event.id).first()[0]
    person_id = auth_client.sqla.query(Person.id).first()[0]
    resp = auth_client.patch(url_for(
        'events.modify_event_participant', event_id=event_id, person_id=person_id), json=payload)
    # THEN we expect an error
    assert resp.status_code == 404
    # GIVEN a database with some linked events and participants
    create_events_participants(auth_client.sqla, 1)
    event_participant = auth_client.sqla.query(EventParticipant).first()
    # WHEN we try to modify an event_participant without a payload
    resp = auth_client.patch(url_for('events.modify_event_participant',
                                     event_id=event_participant.event_id, person_id=event_participant.person_id))
    # THEN we expect the error code
    assert resp.status_code == 422
    # WHEN we modify an event_participant
    resp = auth_client.patch(url_for('events.modify_event_participant',
                                     event_id=event_participant.event_id, person_id=event_participant.person_id),
                             json=payload)
    # THEN we expect the correct code
    assert resp.status_code == 200
    # THEN we expect the event_participant to be modified
    queried_confirmed = auth_client.sqla.query(EventParticipant.confirmed).filter(
        EventParticipant.event_id == event_participant.event_id,
        EventParticipant.person_id == event_participant.person_id).first()[0]
    assert queried_confirmed == payload["confirmed"]


@pytest.mark.smoke
def test_delete_event_participant(auth_client):
    # GIVEN a database with some linked events and participants
    create_multiple_events(auth_client.sqla, 5)
    create_multiple_people(auth_client.sqla, 5)
    create_events_participants(auth_client.sqla, 1)
    event_participant = auth_client.sqla.query(EventParticipant).first()
    count = auth_client.sqla.query(EventParticipant).count()
    # WHEN we unlink an assets from an event
    resp = auth_client.delete(url_for('events.delete_event_participant',
                                      event_id=event_participant.event_id, person_id=event_participant.person_id))
    # THEN we expect the right status code
    assert resp.status_code == 204
    # THEN we expect the linkage to be absent in the database
    assert 0 == auth_client.sqla.query(EventParticipant).filter(
        EventParticipant.event_id == event_participant.event_id,
        EventParticipant.person_id == event_participant.person_id).count()
    # THEN We expect the correct count of link in the database
    new_count = auth_client.sqla.query(EventParticipant).count()
    assert count - 1 == new_count
    # WHEN we unlink the same account again
    resp = auth_client.delete(url_for('events.delete_event_participant',
                                      event_id=event_participant.event_id, person_id=event_participant.person_id))
    # THEN we expect an error
    assert resp.status_code == 404


@pytest.mark.smoke
def test_add_event_images(auth_client):
    # GIVEN a set of events and images
    count = random.randint(3, 6)
    create_multiple_events(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    events = auth_client.sqla.query(Event).all()
    images = auth_client.sqla.query(Image).all()

    # WHEN an image is requested to be tied to each event
    for i in range(count):
        print(i)
        resp = auth_client.post(url_for(
            'events.add_event_images', event_id=events[i].id, image_id=images[i].id))

        # THEN expect the request to run OK
        assert resp.status_code == 201

        # THEN expect the event to have a single image
        assert len(auth_client.sqla.query(Event).filter_by(
            id=events[i].id).first().images) == 1


@pytest.mark.smoke
def test_add_event_images_no_exist(auth_client):
    # GIVEN a set of events and images
    count = random.randint(3, 6)
    create_multiple_events(auth_client.sqla, count)
    create_test_images(auth_client.sqla)

    images = auth_client.sqla.query(Image).all()

    # WHEN a no existent image is requested to be tied to an event
    resp = auth_client.post(
        url_for('events.add_event_images', event_id=1, image_id=len(images) + 1))

    # THEN expect the image not to be found
    assert resp.status_code == 404

    # WHEN an image is requested to be tied to a no existent event
    resp = auth_client.post(
        url_for('events.add_event_images', event_id=count + 1, image_id=1))

    # THEN expect the event not to be found
    assert resp.status_code == 404


@pytest.mark.smoke
def test_add_event_images_already_exist(auth_client):
    # GIVEN a set of events, images, and event_image relationships
    count = random.randint(3, 6)
    create_multiple_events(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_event_images(auth_client.sqla)

    event_images = auth_client.sqla.query(ImageEvent).all()

    # WHEN existing event_image relationships are requested to be created
    for event_image in event_images:
        resp = auth_client.post(url_for(
            'events.add_event_images', event_id=event_image.event_id, image_id=event_image.image_id))

        # THEN expect the request to be unprocessable
        assert resp.status_code == 422


@pytest.mark.smoke
def test_delete_event_image(auth_client):
    # GIVEN a set of events, images, and event_image relationships
    count = random.randint(3, 6)
    create_multiple_events(auth_client.sqla, count)
    create_test_images(auth_client.sqla)
    create_images_events(auth_client.sqla)

    valid_event_image = auth_client.sqla.query(ImageEvent).first()

    # WHEN the event_image relationships are requested to be deleted
    resp = auth_client.delete(url_for('events.delete_event_image',
                                      event_id=valid_event_image.event_id, image_id=valid_event_image.image_id))

    # THEN expect the delete to run OK
    assert resp.status_code == 204


@pytest.mark.smoke
def test_delete_event_image_no_exist(auth_client):
    # GIVEN an empty database

    # WHEN an event_image relationship is requested to be deleted
    resp = auth_client.delete(url_for('events.delete_event_image', event_id=random.randint(
        1, 8), image_id=random.randint(1, 8)))

    # THEN expect the requested row to not be found
    assert resp.status_code == 404
