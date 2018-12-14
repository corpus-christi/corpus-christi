import pytest
import requests

from src.models import I18NLocale

BASE_URL = 'http://localhost:5000/api/v1/i18n'


@pytest.mark.skip
def test_sample(session):
    locale = I18NLocale(id="de", desc="Deutsch")
    session.add(locale)
    session.commit()


@pytest.mark.parametrize('id,desc', [('su', 'Finnish')])
def test_create_valid_locale(id, desc):
    resp = requests.post(f'{BASE_URL}/locales', json={'id': id, 'desc': desc})
    assert resp.status_code == 200
