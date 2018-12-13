import dataset
import pytest
import requests

from config import config

DB_URI = config['test'].SQLALCHEMY_DATABASE_URI
BASE_URL = 'http://localhost:5000/api/v1/i18n/'


@pytest.fixture
def set_up_database():
    db = dataset.connect(DB_URI)
    table = db['i18n_locale']
    table.delete()
    table.insert_many([
        {'id': 'en', 'desc': 'English '},
        {'id': 'es', 'desc': 'Espanol'}
    ])

@pytest.mark.usefixtures('set_up_database')
def test_get_locales():
    resp = requests.get(BASE_URL + 'locales')
    assert resp.status_code == 200
    json = resp.json()
    assert len(json) == 2


@pytest.mark.parametrize('id', ['', 'a', 'a-', '-a', 'aa-', 'aaa-', 'aa-a'])
def test_bogus_locale_ids(id):
    resp = requests.post(BASE_URL + 'locales', data={'id': id, 'desc': id * 2})
    assert resp.status_code == 422
