import dataset
import pytest
import requests

from config import config

DB_URI = config['test'].SQLALCHEMY_DATABASE_URI
BASE_URL = 'http://localhost:5000/api/v1/i18n'

db = dataset.connect(DB_URI)
locale_table = db['i18n_locale']
key_table = db['i18n_key']
value_table = db['i18n_value']

locale_data = [
    {'id': 'en', 'desc': 'English'},
    {'id': 'es', 'desc': 'Español'}
]
locale_tuples = [(loc['id'], loc['desc']) for loc in locale_data]

key_data = [
    {'id': 'app.name', 'desc': 'Application name'},
    {'id': 'courses.name', 'desc': 'Name of the courses module'},
    {'id': 'btn.ok', 'desc': 'Label on an OK button'},
    {'id': 'label.name.first', 'desc': 'Label for a first name prompt'},
    {'id': 'label.name.last', 'desc': 'Label for a last name prompt'}
]
key_tuples = [(val['id'], val['desc']) for val in key_data]

value_data = []
for locale in locale_data:
    for key in key_data:
        value_data.append({
            'locale_id': locale['id'],
            'key_id': key['id'],
            'gloss': f"{key['desc']} in {locale['desc']}"
        })


def _delete_data():
    value_table.delete()
    locale_table.delete()
    key_table.delete()


def _load_data():
    locale_table.insert_many(locale_data)
    key_table.insert_many(key_data)
    value_table.insert_many(value_data)


@pytest.fixture
def delete_data():
    db.begin()
    _delete_data()
    db.commit()


@pytest.fixture
def load_data():
    db.begin()
    _delete_data()
    _load_data()
    db.commit()


# ---- Locales

@pytest.mark.usefixtures('load_data')
def test_read_all_locales():
    resp = requests.get(f'{BASE_URL}/locales')
    assert resp.status_code == 200
    json = resp.json()
    assert len(json) == len(locale_data)


@pytest.mark.usefixtures('load_data')
@pytest.mark.parametrize('id,desc', locale_tuples)
def test_read_existing_locale(id, desc):
    resp = requests.get(f'{BASE_URL}/locales/{id}')
    assert resp.status_code == 200
    assert resp.json()['desc'] == desc


@pytest.mark.parametrize('id', ['', 'a', 'aa', 'aaa', 'aa-aa'])
def test_read_nonexistent_locale(id):
    resp = requests.get(f'{BASE_URL}/locales/{id}')
    assert resp.status_code == 404


@pytest.mark.parametrize('id', ['', 'a', 'a-', '-a', 'aa-', 'aaa-', 'aa-a'])
def test_create_bogus_locale(id):
    resp = requests.post(f'{BASE_URL}/locales', json={'id': id, 'desc': id * 2})
    assert resp.status_code == 422


@pytest.mark.usefixtures('delete_data')
@pytest.mark.parametrize('id,desc', locale_tuples)
def test_create_valid_locale(id, desc):
    resp = requests.post(f'{BASE_URL}/locales', json={'id': id, 'desc': desc})
    assert resp.status_code == 200


# ---- Keys

@pytest.mark.usefixtures('load_data')
def test_read_all_keys():
    resp = requests.get(f'{BASE_URL}/keys')
    assert resp.status_code == 200
    json = resp.json()
    assert len(json) == len(key_data)


# @pytest.mark.usefixtures('load_data')
@pytest.mark.parametrize('id,desc', key_tuples)
def test_read_existing_key(id, desc):
    resp = requests.get(f'{BASE_URL}/keys/{id}')
    assert resp.status_code == 200
    assert resp.json()['desc'] == desc


@pytest.mark.parametrize('id', ['', 'a', 'aa', 'aaa', 'aa-aa'])
def test_read_nonexistent_key(id):
    resp = requests.get(f'{BASE_URL}/keys/{id}')
    assert resp.status_code == 404


@pytest.mark.parametrize('id', ['', 'a', 'a-', '-a', 'aa-', 'aaa-', 'aa-a'])
def test_create_bogus_key(id):
    resp = requests.post(f'{BASE_URL}/keys', json={'id': id, 'desc': id * 2})
    assert resp.status_code == 422


@pytest.mark.usefixtures('delete_data')
@pytest.mark.parametrize('id,desc', key_tuples)
def test_create_valid_key(id, desc):
    resp = requests.post(f'{BASE_URL}/keys', json={'id': id, 'desc': desc})
    assert resp.status_code == 200
    assert key_table.count() == 1


# ---- Values

@pytest.mark.usefixtures('load_data')
def test_read_all_values():
    resp = requests.get(f'{BASE_URL}/values')
    assert resp.status_code == 200
    assert len(resp.json()) == len(locale_data) * len(key_data)

