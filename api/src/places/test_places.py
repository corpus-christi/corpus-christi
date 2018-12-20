import pytest
from flask import url_for

from src.places.models import Country


@pytest.mark.parametrize('code, name', [('US', 'United States'),
                                        ('EC', 'Ecuador'),
                                        ('TH', 'Thailand')])
def test_read_country(client, dbs, code, name):
    count = Country.load_from_file()
    print(f"READ {count} COUNTRIES")
    assert count > 0
    resp = client.get(url_for('places.read_countries', country_code=code, locale='en-US'))
    assert resp.status_code == 200
    print("RESP", resp.json)
    assert resp.json['name'] == name


def test_read_all_countries(client, dbs):
    count = Country.load_from_file()
    print(f"READ {count} COUNTRIES")
    assert count > 0
    resp = client.get(url_for('places.read_countries', locale='en-US'))
    assert resp.status_code == 200
    assert len(resp.json) == count
