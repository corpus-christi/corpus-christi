import pytest
from flask import url_for

from .models import Country


@pytest.mark.slow
@pytest.mark.parametrize('code, name', [('US', 'United States'),
                                        ('EC', 'Ecuador'),
                                        ('TH', 'Thailand')])
def test_read_country(auth_client, code, name):
    count = Country.load_from_file()
    assert count > 0
    resp = auth_client.get(url_for('places.read_countries', country_code=code, locale='en-US'))
    assert resp.status_code == 200
    print("RESP", resp.json)
    assert resp.json['name'] == name


@pytest.mark.slow
def test_read_all_countries(auth_client):
    count = Country.load_from_file()
    assert count > 0
    resp = auth_client.get(url_for('places.read_countries', locale='en-US'))
    assert resp.status_code == 200
    assert len(resp.json) == count


@pytest.mark.smoke
def test_missing_locale(auth_client):
    resp = auth_client.get(url_for('places.read_countries'))
    assert resp.status_code == 400

    resp = auth_client.get(url_for('places.read_countries', country_code='US'))
    assert resp.status_code == 400
