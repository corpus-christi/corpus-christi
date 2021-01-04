import os
import random
from io import BytesIO

import pytest
from flask import url_for

from .create_image_data import fake, flip, create_multiple_images
from .models import Image
from .. import API_DIR


# ---- Group


@pytest.mark.smoke
def test_download_image(auth_client):
    # GIVEN some randomly created images
    count = random.randint(3, 7)
    create_multiple_images(auth_client.sqla, count)

    images = auth_client.sqla.query(Image).all()
    # WHEN we ask for the events one by one
    for image in images:
        with open(API_DIR + '/' + image.path, 'rb') as img:
            img_string_io = BytesIO(img.read())
        resp = auth_client.get(
            url_for('images.download_image', image_id=image.id))
        # THEN we expect each of them to correspond grab an image in the file
        # system
        assert resp.status_code == 200
        assert resp.data == img_string_io.read()


@pytest.mark.smoke
def test_download_invalid_image(auth_client):
    # GIVEN some randomly created images
    count = random.randint(3, 7)
    create_multiple_images(auth_client.sqla, count)

    fake_image_id = -1
    # WHEN we ask for an invalid image
    resp = auth_client.get(
        url_for('images.download_image', image_id=fake_image_id))
    # THEN we expect to get a 404
    assert resp.status_code == 404


@pytest.mark.smoke
def test_upload_image(auth_client):
    # GIVEN an empty database
    # WHEN we upload an image
    create_multiple_images(auth_client.sqla, 1)
    # THEN we can see an image in the database
    resp = auth_client.get(url_for('images.download_image', image_id=1))
    assert resp.status_code == 200


@pytest.mark.smoke
def test_update_image(auth_client):
    # GIVEN some randomly created images
    count = random.randint(3, 7)
    create_multiple_images(auth_client.sqla, count)

    images = auth_client.sqla.query(Image).all()
    # WHEN we update the description for the events one by one
    for image in images:
        expected_status_code = 200

        payload = {
            'description': fake.word()
        }

        if flip():
            payload['description'] = None

        if flip():
            expected_status_code = 422
            payload['fake'] = None

        resp = auth_client.patch(
            url_for('images.update_image', image_id=image.id), json=payload)
        # THEN we expect each of them to correspond grab an image in the file
        # system
        assert resp.status_code == expected_status_code
        if expected_status_code == 200:
            assert resp.json['description'] == payload['description']


@pytest.mark.smoke
def test_delete_image(auth_client):
    # GIVEN some randomly created images
    count = random.randint(3, 7)
    create_multiple_images(auth_client.sqla, count)

    images = auth_client.sqla.query(Image).all()
    # WHEN we ask for the events one by one
    for image in images:
        resp = auth_client.delete(
            url_for('images.delete_image', image_id=image.id))
        # THEN we expect a 204 and for the image to not be in the db or file
        # system
        assert resp.status_code == 204
        assert len(auth_client.sqla.query(
            Image).filter_by(id=image.id).all()) == 0
        assert not os.path.exists(API_DIR + '/' + image.path)


@pytest.mark.smoke
def test_delete_invalid_image(auth_client):
    # GIVEN some randomly created images
    count = random.randint(3, 7)
    create_multiple_images(auth_client.sqla, count)

    fake_image_id = -1
    # WHEN we ask for an invalid image
    resp = auth_client.delete(
        url_for('images.delete_image', image_id=fake_image_id))
    # THEN we expect to get a 404
    assert resp.status_code == 404
