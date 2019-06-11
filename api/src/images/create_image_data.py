import datetime
import math
import random

import pytest
from faker import Faker
from flask import url_for
from flask_jwt_extended import create_access_token
from werkzeug.datastructures import Headers
from werkzeug.security import check_password_hash

from ..courses.models import Course, CourseSchema
from ..events.models import Event, EventSchema
from ..groups.models import Group, GroupSchema
from ..people.models import Person, PersonSchema
from ..places.models import Location, LocationSchema
from .models import (Image, ImageCourse, ImageCourseSchema, ImageEvent,
                     ImageEventSchema, ImageGroup, ImageGroupSchema,
                     ImageLocation, ImageLocationSchema, ImagePerson,
                     ImagePersonSchema, ImageSchema)


class RandomLocaleFaker:
    """Generate multiple fakers for different locales."""

    def __init__(self, *locales):
        self.fakers = [Faker(loc) for loc in locales]

    def __call__(self):
        """Return a random faker."""
        return random.choice(self.fakers)


rl_fake = RandomLocaleFaker('en_US', 'es_MX')
fake = Faker()  # Generic faker; random-locale ones don't implement everything.

# Sample images
valid_paths = ['images/a1/casa.jpg', 'images/a1/coffee_house.jpg', 'images/a1/park.jpg', 'images/a1/verbo.jpg',
               'images/m5/downtown.jpg', 'images/m5/park.jpg', 'images/m5/broken_bridge.jpg', 'images/m5/tree.jpg']
paths_taken = [False, False, False, False, False, False, False, False]

# Used in create_multiple_images to guarentee that the program won't die due to an IndexOutOfRange with uneven array lengths
num_valid_images = len(valid_paths) if len(
    valid_paths) < len(paths_taken) else len(paths_taken)


def flip():
    """Return true or false randomly."""
    return random.choice((True, False))


def reset_paths_taken():
    for i in range(0, len(paths_taken)):
        paths_taken[i] = False


# Used to create the test images in the database; pulled from Events
def create_test_images(sqla):
    image_schema = ImageSchema()
    new_images = []

    valid_image = image_schema.load(
        {'path': 'image/a1/casa.jpg', 'description': 'Civil authority rich coach answer total general.'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load({'path': 'image/a1/coffee_house.jpg'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load({'path': 'image/a1/park.jpg'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load({'path': 'image/a1/verbo.jpg'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load({'path': 'image/m5/downtown.jpg'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load(
        {'path': 'image/m5/park.jpg', 'description': 'Explicabo doloremque voluptatibus quaerat repellat libero.'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load({'path': 'image/m5/broken_bridge.jpg'})
    new_images.append(Image(**valid_image))
    valid_image = image_schema.load(
        {'path': 'image/m5/tree.jpg', 'description': 'Factor rate forget research today hand.'})
    new_images.append(Image(**valid_image))

    sqla.add_all(new_images)
    sqla.commit()


def image_object_factory(sqla):
    """Cook up a fake image."""

    # Getting a valid path name
    i = 0

    while(paths_taken[i]):
        i += 1
        if i == len(paths_taken):
            i = 0
            reset_paths_taken()
            continue

    paths_taken[i] = True

    image = {
        'path': valid_paths[i]
    }

    file = open(valid_paths[i], 'w')
    file.close()

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


def image_person_object_factory(image_id, person_id):
    """Cook up a fake imageperson json object from given ids."""
    personimage = {
        'image_id': image_id,
        'person_id': person_id
    }
    return personimage


def image_course_object_factory(image_id, course_id):
    """Cook up a fake imagecourse json object from given ids."""
    courseimage = {
        'image_id': image_id,
        'course_id': course_id
    }
    return courseimage


def image_group_object_factory(image_id, group_id):
    """Cook up a fake imagegroup json object from given ids."""
    groupimage = {
        'image_id': image_id,
        'group_id': group_id
    }
    return groupimage


def image_location_object_factory(image_id, location_id):
    """Cook up a fake imagelocation json object from given ids."""
    locationimage = {
        'image_id': image_id,
        'location_id': location_id
    }
    return locationimage


def create_multiple_images(sqla, n):
    """Commit `n` new images (up to len(valid_paths) to the database. Return their IDs."""
    image_schema = ImageSchema()
    new_images = []
    for i in range(n):
        if (i < num_valid_images):
            valid_images = image_schema.load(image_object_factory(sqla))
            new_images.append(Image(**valid_images))
    sqla.add_all(new_images)
    sqla.commit()


def create_images_events(sqla, fraction=0.75):
    """Create data in the linking table between images and events """
    image_event_schema = ImageEventSchema()
    new_images_events = []
    if not sqla.query(Image).all():
        create_multiple_images(sqla, random.randint(3, 6))
    if not sqla.query(Event).all():
        create_multiple_events(sqla, random.randint(3, 6))
    all_images_events = sqla.query(Image, Event).all()
    sample_images_events = random.sample(
        all_images_events, math.floor(len(all_images_events) * fraction))
    for image_event in sample_images_events:
        valid_image_event = image_event_schema.load(
            image_event_object_factory(image_event[0].id, image_event[1].id))
        new_images_events.append(ImageEvent(**valid_image_event))
    sqla.add_all(new_images_events)
    sqla.commit()


def create_images_people(sqla, fraction=0.75):
    """Create data in the linking table between images and people """
    image_person_schema = ImagePersonSchema()
    new_images_people = []
    if not sqla.query(Image).all():
        create_multiple_images(sqla, random.randint(3, 6))
    if not sqla.query(Person).all():
        create_multiple_people(sqla, random.randint(3, 6))
    all_images_people = sqla.query(Image, Person).all()
    sample_images_people = random.sample(
        all_images_people, math.floor(len(all_images_people) * fraction))
    for image_person in sample_images_people:
        valid_image_person = image_person_schema.load(
            image_person_object_factory(image_person[0].id, image_person[1].id))
        new_images_people.append(ImagePerson(**valid_image_person))
    sqla.add_all(new_images_people)
    sqla.commit()


def create_images_courses(sqla, fraction=0.75):
    """Create data in the linking table between images and images"""
    image_course_schema = ImageCourseSchema()
    new_images_courses = []
    if not sqla.query(Image).all():
        create_multiple_images(sqla, random.randint(3, 6))
    if not sqla.query(Course).all():
        create_multiple_courses(sqla, random.randint(3, 6))
    all_images_courses = sqla.query(Image, Course).all()
    sample_images_courses = random.sample(
        all_images_courses, math.floor(len(all_images_courses) * fraction))
    for image_course in sample_images_courses:
        valid_image_course = image_course_schema.load(
            image_course_object_factory(image_course[0].id, image_course[1].id))
        new_images_courses.append(ImageCourse(**valid_image_course))
    sqla.add_all(new_images_courses)
    sqla.commit()


def create_images_groups(sqla, fraction=0.75):
    """Create data in the linking table between images and groups"""
    image_group_schema = ImageGroupSchema()
    new_images_groups = []
    if not sqla.query(Image).all():
        create_multiple_images(sqla, random.randint(3, 6))
    if not sqla.query(Group).all():
        create_multiple_groups(sqla, random.randint(3, 6))
    all_images_groups = sqla.query(Image, Group).all()
    sample_images_groups = random.sample(
        all_images_groups, math.floor(len(all_images_groups) * fraction))
    for image_group in sample_images_groups:
        valid_image_group = image_group_schema.load(
            image_group_object_factory(image_group[0].id, image_group[1].id))
        new_images_groups.append(ImageGroup(**valid_image_group))
    sqla.add_all(new_images_groups)
    sqla.commit()


def create_images_locations(sqla, fraction=0.75):
    """Create data in the linking table between images and locations"""
    image_location_schema = ImageLocationSchema()
    new_images_locations = []
    if not sqla.query(Image).all():
        create_multiple_images(sqla, random.randint(3, 6))
    if not sqla.query(Location).all():
        create_multiple_locations(sqla, random.randint(3, 6))
    all_images_locations = sqla.query(Image, Location).all()
    sample_images_locations = random.sample(
        all_images_locations, math.floor(len(all_images_locations) * fraction))
    for image_location in sample_images_locations:
        valid_image_location = image_location_schema.load(
            image_location_object_factory(image_location[0].id, image_location[1].id))
        new_images_locations.append(ImageLocation(**valid_image_location))
    sqla.add_all(new_images_locations)
    sqla.commit()


def create_images_test_data(sqla):
    """The function that creates test data in the correct order """
    create_multiple_images(sqla, 15)
    create_images_events(sqla, 0.75)
    create_images_people(sqla, 0.75)
    create_images_courses(sqla, 0.75)
    create_images_groups(sqla, 0.75)
    create_images_locations(sqla, 0.75)
