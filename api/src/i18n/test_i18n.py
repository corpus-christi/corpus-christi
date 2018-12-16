import pytest
from flask import url_for

from src.models import I18NLocale, I18NKey, I18NValue

locale_data = [
    {'id': 'en', 'desc': 'English'},
    {'id': 'es', 'desc': 'Español'}
]
locale_tuples = [(loc['id'], loc['desc']) for loc in locale_data]


def create_locales(dbs):
    dbs.add_all([I18NLocale(**d) for d in locale_data])
    dbs.commit()


key_data = [
    {'id': 'app.name', 'desc': 'Application name'},
    {'id': 'courses.name', 'desc': 'Name of the courses module'},
    {'id': 'btn.ok', 'desc': 'Label on an OK button'},
    {'id': 'label.name.first', 'desc': 'Label for a first name prompt'},
    {'id': 'label.name.last', 'desc': 'Label for a last name prompt'}
]
key_tuples = [(val['id'], val['desc']) for val in key_data]


def create_keys(dbs):
    dbs.add_all([I18NKey(**k) for k in key_data])
    dbs.commit()


# value_data = []
# for locale in locale_data:
#     for key in key_data:
#         value_data.append({
#             'locale_id': locale['id'],
#             'key_id': key['id'],
#             'gloss': f"{key['desc']} in {locale['desc']}"
#         })

def create_values(dbs):
    for locale in locale_data:
        for key in key_data:
            val = I18NValue(locale_id=locale['id'],
                            key_id=key['id'],
                            gloss=f"{key['desc']} in {locale['desc']}")
            dbs.add(val)
    dbs.commit()

# ---- Locales

def test_read_all_locales(client, dbs):
    create_locales(dbs)
    resp = client.get(url_for('i18n.read_all_locales'))
    assert resp.status_code == 200
    assert len(resp.json) == len(locale_data)


@pytest.mark.parametrize('id, desc', locale_tuples)
def test_read_one_locale(client, dbs, id, desc):
    create_locales(dbs)
    resp = client.get(url_for('i18n.read_one_locale', locale_id=id))
    assert resp.status_code == 200
    assert resp.json['id'] == id
    assert resp.json['desc'] == desc


@pytest.mark.parametrize('id', ['', 'a', 'aa', 'aaa', 'aa-aa'])
def test_read_nonexistent_locale(client, id):
    resp = client.get(url_for('i18n.read_one_locale', locale_id=id))
    assert resp.status_code == 404


@pytest.mark.parametrize('id', ['', 'a', 'a-', '-a', 'aa-', 'aaa-', 'aa-a'])
def test_create_bogus_locale(client, id):
    resp = client.post(url_for('i18n.create_locale'),
                       json={'id': id, 'desc': id * 2})
    assert resp.status_code == 422


@pytest.mark.usefixtures('orm')
@pytest.mark.parametrize('id, desc', locale_tuples)
def test_create_valid_locale(client, id, desc):
    resp = client.post(url_for('i18n.create_locale'),
                       json={'id': id, 'desc': desc})
    assert resp.status_code == 200


# ---- Keys

def test_read_all_keys(client, dbs):
    create_keys(dbs)
    resp = client.get(url_for('i18n.read_all_keys'))
    assert resp.status_code == 200
    assert len(resp.json) == len(key_data)


@pytest.mark.parametrize('id, desc', key_tuples)
def test_read_existing_key(client, dbs, id, desc):
    create_keys(dbs)
    resp = client.get(url_for('i18n.read_one_key', key_id=id))
    assert resp.status_code == 200
    assert resp.json['desc'] == desc


@pytest.mark.parametrize('id', ['', 'a', 'aa', 'aaa', 'aa-aa'])
def test_read_nonexistent_key(client, id):
    resp = client.get(url_for('i18n.read_one_key', key_id=id))
    assert resp.status_code == 404


@pytest.mark.parametrize('id', ['', 'a', 'a-', '-a', 'aa-', 'aaa-', 'aa-a'])
def test_create_bogus_key(client, id):
    resp = client.post(url_for('i18n.create_key'),
                       json={'id': id, 'desc': id * 2})
    assert resp.status_code == 422


@pytest.mark.usefixtures('orm')
@pytest.mark.parametrize('id,desc', key_tuples)
def test_create_valid_key(client, id, desc):
    resp = client.post(url_for('i18n.create_key'),
                       json={'id': id, 'desc': desc})
    assert resp.status_code == 200


# ---- Values

def test_read_all_values(client, dbs):
    create_values(dbs)
    resp = client.get(url_for('i18n.read_all_values'))
    assert resp.status_code == 200
    assert len(resp.json) == len(locale_data) * len(key_data)
