import pytest
from flask import url_for

from src.i18n.models import Language


@pytest.mark.parametrize('code, name', [('en', 'English'),
                                        ('th', 'Thai'),
                                        ('es', 'Spanish; Castilian')])
def test_read_language(client, dbs, code, name):
    count = Language.load_from_file()
    resp = client.get(url_for('i18n.read_languages', language_code=code, locale='en-US'))
    assert resp.status_code == 200
    assert resp.json['name'] == name


def test_read_all_languages(client, dbs):
    count = Language.load_from_file()
    resp = client.get(url_for('i18n.read_languages', locale='en-US'))
    assert resp.status_code == 200
    assert len(resp.json) == count
