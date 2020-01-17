import math
import random

from faker import Faker

from .models import Event, EventPerson, EventParticipant, EventSchema, EventPersonSchema, EventParticipantSchema
from .models import EventAsset, EventAssetSchema, EventTeam, EventTeamSchema
from ..assets.models import Asset, AssetSchema
from ..images.models import Image, ImageEvent, ImageEventSchema
from ..people.models import Person
from ..places.models import Location
from ..places.test_places import create_multiple_locations
from ..teams.models import Team, TeamMember, TeamSchema, TeamMemberSchema


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


def event_object_factory(sqla):
    """Cook up a fake event."""
    event = {
        'title': rl_fake().word(),
        'start': str(rl_fake().future_datetime(end_date="+3d")),
        'end': str(rl_fake().date_time_between(start_date="+3d", end_date="+4d", tzinfo=None)),
        'active': flip(),
        'aggregate': flip()
    }

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        event['description'] = rl_fake().sentences(nb=1)[0]
    if flip():
        all_locations = sqla.query(Location).all()
        if len(all_locations) > 0:
            event['location_id'] = all_locations[random.randint(0, len(all_locations) - 1)].id
    if flip():
        event['attendance'] = random.randint(0, 1500)
    return event


def event_object_factory_approx_one_week_ago(sqla):
    """Cook up a fake event."""
    event = {
        'title': rl_fake().word(),
        'start': str(rl_fake().date_time_between(start_date="-1w", end_date="-3d", tzinfo=None)),
        'end': str(rl_fake().date_time_between(start_date="-3d", end_date="+0d", tzinfo=None)),
        'active': flip(),
        'aggregate': flip()
    }

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        event['description'] = rl_fake().sentences(nb=1)[0]
    if flip():
        all_locations = sqla.query(Location).all()
        if len(all_locations) > 0:
            event['location_id'] = all_locations[random.randint(0, len(all_locations) - 1)].id
    if flip():
        event['attendance'] = random.randint(0, 1500)
    return event


def event_object_factory_long_ago(sqla):
    """Cook up a fake event."""
    event = {
        'title': rl_fake().word(),
        'start': str(rl_fake().date_time_between(start_date="-11y", end_date="-1m", tzinfo=None)),
        'end': str(rl_fake().date_time_between(start_date="-1m", end_date="+0d", tzinfo=None)),
        'active': flip(),
        'aggregate': flip()
    }

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        event['description'] = rl_fake().sentences(nb=1)[0]
    if flip():
        all_locations = sqla.query(Location).all()
        if len(all_locations) > 0:
            event['location_id'] = all_locations[random.randint(0, len(all_locations) - 1)].id
    if flip():
        event['attendance'] = random.randint(0, 1500)
    return event


def asset_object_factory(sqla):
    """Cook up a fake asset."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    all_locations = sqla.query(Location).all()
    if not all_locations:
        create_multiple_locations(sqla, random.randint(3, 6))
        all_locations = sqla.query(Location).all()
    asset = {
        'description': rl_fake().sentences(nb=1)[0],
        'location_id': all_locations[random.randint(0, len(all_locations) - 1)].id,
        'active': flip()
    }
    return asset


def team_object_factory():
    """Cook up a fake asset."""
    fake = Faker()  # Use a generic one; others may not have all methods.
    team = {
        'description': rl_fake().sentences(nb=1)[0],
        'active': flip()
    }
    return team


def email_object_factory():
    email = {
        'subject': 'Test Email',
        'body': rl_fake().sentences(nb=1)[0],
        'recipients': ['tim_ours@taylor.edu']
    }

    return email


def event_asset_object_factory(event_id, asset_id):
    """Cook up a fake eventasset json object from given ids."""
    eventasset = {
        'event_id': event_id,
        'asset_id': asset_id
    }
    return eventasset


def event_team_object_factory(event_id, team_id):
    """Cook up a fake eventteam json object from given ids."""
    eventteam = {
        'event_id': event_id,
        'team_id': team_id
    }
    return eventteam


def event_participant_object_factory(event_id, person_id):
    """Cook up a fake eventteam json object from given ids."""
    eventparticipant = {
        'event_id': event_id,
        'person_id': person_id,
        'confirmed': flip()
    }
    return eventparticipant


def event_person_object_factory(event_id, person_id):
    """Cook up a fake eventteam json object from given ids."""
    eventperson = {
        'event_id': event_id,
        'person_id': person_id,
        'description': rl_fake().sentences(nb=1)[0],
    }
    return eventperson


def team_member_object_factory(team_id, member_id):
    """Cook up a fake eventteam json object from given ids."""
    teammember = {
        'team_id': team_id,
        'member_id': member_id,
        'active': flip()
    }
    return teammember


def create_multiple_events(sqla, n):
    """Commit `n` nfw events to the database. Return their IDs."""
    event_schema = EventSchema()
    new_events = []
    for i in range(n):
        factory = event_object_factory
        if flip():
            factory = event_object_factory_long_ago
        elif flip():
            factory = event_object_factory_approx_one_week_ago
        valid_events = event_schema.load(factory(sqla))
        new_events.append(Event(**valid_events))
    sqla.add_all(new_events)
    sqla.commit()


def create_multiple_teams(sqla, n):
    """Commit `n` new teams to the database. Return their IDs."""
    team_schema = TeamSchema()
    new_teams = []
    for i in range(n):
        valid_teams = team_schema.load(team_object_factory())
        new_teams.append(Team(**valid_teams))
    sqla.add_all(new_teams)
    sqla.commit()


def create_multiple_assets(sqla, n):
    """Commit `n` new assets to the database. Return their IDs."""
    asset_schema = AssetSchema()
    new_assets = []
    for i in range(n):
        valid_assets = asset_schema.load(asset_object_factory(sqla))
        new_assets.append(Asset(**valid_assets))
    sqla.add_all(new_assets)
    sqla.commit()


def create_events_assets(sqla, fraction=0.75):
    """Create data in the linking table between events and assets """
    event_asset_schema = EventAssetSchema()
    new_events_assets = []
    all_events = sqla.query(Event).all()
    if not all_events:
        create_multiple_events(sqla, random.randint(3, 6))
        all_events = sqla.query(Event).all()
    all_assets = sqla.query(Asset).all()
    if not all_assets:
        create_multiple_assets(sqla, random.randint(3, 6))
        all_assets = sqla.query(Asset).all()
    all_events_assets = sqla.query(Event, Asset).all()
    sample_events_assets = random.sample(all_events_assets, math.floor(len(all_events_assets) * fraction))
    for events_assets in sample_events_assets:
        valid_events_assets = event_asset_schema.load(
            event_asset_object_factory(events_assets[0].id, events_assets[1].id))
        new_events_assets.append(EventAsset(**valid_events_assets))
    sqla.add_all(new_events_assets)
    sqla.commit()


def create_events_teams(sqla, fraction=0.75):
    """Create data in the linking table between events and teams """
    event_team_schema = EventTeamSchema()
    new_events_teams = []
    all_events = sqla.query(Event).all()
    if not all_events:
        create_multiple_events(sqla, random.randint(3, 6))
        all_events = sqla.query(Event).all()
    all_teams = sqla.query(Team).all()
    if not all_teams:
        create_multiple_teams(sqla, random.randint(3, 6))
        all_assets = sqla.query(Team).all()
    all_events_teams = sqla.query(Event, Team).all()
    sample_events_teams = random.sample(all_events_teams, math.floor(len(all_events_teams) * fraction))
    for events_teams in sample_events_teams:
        valid_events_teams = event_team_schema.load(event_team_object_factory(events_teams[0].id, events_teams[1].id))
        new_events_teams.append(EventTeam(**valid_events_teams))
    sqla.add_all(new_events_teams)
    sqla.commit()


def create_events_participants(sqla, fraction=0.75):
    """Create data in the linking table between events and participants """
    event_participant_schema = EventParticipantSchema()
    new_events_participants = []
    all_events = sqla.query(Event).all()
    if not all_events:
        create_multiple_events(sqla, random.randint(3, 6))
        all_events = sqla.query(Event).all()
    all_participants = sqla.query(Person).all()
    if not all_participants:
        create_multiple_people(sqla, random.randint(3, 6))
        all_participants = sqla.query(Person).all()
    all_events_participants = sqla.query(Event, Person).all()
    sample_events_participants = random.sample(all_events_participants,
                                               math.floor(len(all_events_participants) * fraction))
    for events_participants in sample_events_participants:
        valid_events_participants = event_participant_schema.load(
            event_participant_object_factory(events_participants[0].id, events_participants[1].id))
        new_events_participants.append(EventParticipant(**valid_events_participants))
    sqla.add_all(new_events_participants)
    sqla.commit()


def create_events_persons(sqla, fraction=0.75):
    """Create data in the linking table between events and persons """
    event_person_schema = EventPersonSchema()
    new_events_persons = []
    all_events = sqla.query(Event).all()
    if not all_events:
        create_multiple_events(sqla, random.randint(3, 6))
        all_events = sqla.query(Event).all()
    all_people = sqla.query(Person).all()
    if not all_people:
        create_multiple_people(sqla, random.randint(3, 6))
        all_people = sqla.query(Person).all()
    all_events_persons = sqla.query(Event, Person).all()
    sample_events_persons = random.sample(all_events_persons, math.floor(len(all_events_persons) * fraction))
    for events_persons in sample_events_persons:
        valid_events_persons = event_person_schema.load(
            event_person_object_factory(events_persons[0].id, events_persons[1].id))
        new_events_persons.append(EventPerson(**valid_events_persons))
    sqla.add_all(new_events_persons)
    sqla.commit()


def create_teams_members(sqla, fraction=0.75):
    """Create data in the linking table between teams and members """
    team_member_schema = TeamMemberSchema()
    new_teams_members = []
    all_teams_members = sqla.query(Team, Person).all()
    sample_teams_members = random.sample(all_teams_members, math.floor(len(all_teams_members) * fraction))
    for teams_members in sample_teams_members:
        valid_teams_members = team_member_schema.load(
            team_member_object_factory(teams_members[0].id, teams_members[1].id))
        new_teams_members.append(TeamMember(**valid_teams_members))
    sqla.add_all(new_teams_members)
    sqla.commit()


def create_events_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_events(sqla, 300)
    create_multiple_assets(sqla, 12)
    create_multiple_teams(sqla, 13)
    create_events_assets(sqla, 0.75)
    create_events_teams(sqla, 0.75)
    create_events_participants(sqla, 0.75)
    create_events_persons(sqla, 0.75)
    create_teams_members(sqla, 0.75)


def get_team_ids(teams):
    ids = []
    for team in teams:
        ids.append(team['id'])
    return ids


# Create a team in database, return the id
def create_team(sqla, description, active=True):
    team_schema = TeamSchema()
    team_payload = {
        'description': description,
        'active': active
    }
    valid_team = team_schema.load(team_payload)
    team = Team(**valid_team)
    sqla.add(team)
    sqla.commit()
    return team.id


def create_event(sqla, title, description, start, end, location_id=None, active=True):
    event_schema = EventSchema()
    event_payload = {
        'title': title,
        'description': description,
        'start': str(start),
        'end': str(end),
        'active': active
    }
    if location_id:
        event_payload['location_id'] = location_id
    valid_event = event_schema.load(event_payload)
    event = Event(**valid_event)
    sqla.add(event)
    sqla.commit()
    return event.id


def create_event_person(sqla, event_id, person_id, description):
    event_person_schema = EventPersonSchema()
    event_person_payload = {
        'event_id': event_id,
        'person_id': person_id,
        'description': description
    }
    valid_event_person = event_person_schema.load(event_person_payload)
    event_person = EventPerson(**valid_event_person)
    sqla.add(event_person)
    sqla.commit()
    return event_person_payload


def create_event_participant(sqla, event_id, person_id, confirmed=True):
    event_participant_schema = EventParticipantSchema()
    event_participant_payload = {
        'event_id': event_id,
        'person_id': person_id,
        'confirmed': confirmed
    }
    valid_event_participant = event_participant_schema.load(event_participant_payload)
    event_participant = EventParticipant(**valid_event_participant)
    sqla.add(event_participant)
    sqla.commit()
    return event_participant_payload


def create_event_images(sqla):
    image_event_schema = ImageEventSchema()
    events = sqla.query(Event).all()
    if not events:
        create_multiple_events(sqla, random.randint(3, 6))
        events = sqla.query(Event).all()
    images = sqla.query(Image).all()
    if not images:
        create_multiple_images(sqla, random.randint(3, 6))
        events = sqla.query(Event).all()

    count = len(events)
    if len(images) < len(events):
        count = len(images)

    new_event_images = []

    for i in range(count):
        valid_event_image = image_event_schema.load({'event_id': events[i].id, 'image_id': images[i].id})
        new_event_images.append(ImageEvent(**valid_event_image))

    sqla.add_all(new_event_images)
    sqla.commit()
