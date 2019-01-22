import math
import random

import pytest
import datetime
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from .models import Image, ImageSchema, ImageEvent, ImageEventSchema
from ..events.models import Event, EventSchema

class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')
fake = Faker()  # Generic faker; random-locale ones don't implement everything.

valid_paths = ['data/a1/casa.jpg', 'data/a1/coffee_house.jpg', 'data/a1/park.jpg', 'data/a1/verbo.jpg', 'data/m5/downtown.jpg', 'data/m5/park.jpg', 'data/m5/broken_bridge.jpg', 'data/m5/tree.jpg']
paths_taken = [False, False, False, False, False, False, False, False]

def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def image_object_factory(sqla):
    """Cook up a fake image."""
    
    #Getting a valid path name
    i = 0;
    while(paths_taken[i]):
        i += 1
    paths_taken[i] = True

    image = {
        'path': valid_paths[i]
    }

    # These are all optional in the DB. Over time, we'll try all possibilities.
    if flip():
        image['description'] = rl_fake().sentences(nb=1)[0]
    return image


def image_event_object_factory(image_id, event_id):
    """Cook up a fake imageevent json object from given ids."""
    eventimage = {
        'image_id': image_id,
        'event_id': event_id
    }
    return eventimage

def create_multiple_images(sqla, n):
    """Commit `n` new images (up to len(valid_paths) to the database. Return their IDs."""
    image_schema = ImageSchema()
    new_images = []
    for i in range(n):
        if (i < len(valid_paths)):
            valid_images = image_schema.load(image_object_factory(sqla))
            new_images.append(Image(**valid_images))
    sqla.add_all(new_images)
    sqla.commit()

def create_images_events(sqla, fraction=0.75):
    """Create data in the linking table between images and events """
    image_event_schema = ImageEventSchema()
    new_images_events = []
    all_images_events = sqla.query(Image, Event).all()
    sample_images_events = random.sample(all_images_events, math.floor(len(all_images_events) * fraction))
    for image_event in sample_images_events:
        valid_image_event = image_event_schema.load(image_event_object_factory(image_event[0].id,image_event[1].id))
        new_images_events.append(ImageEvent(**valid_image_event))
    sqla.add_all(new_images_events)
    sqla.commit()


def create_images_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_images(sqla, 15)
    create_images_events(sqla, 0.75)
