import pytest
from flask import url_for

from src.models import I18NLocale, I18NKey, I18NValue

locale_data = [
    {'id': 'en', 'desc': 'English', 'country': 'us'},
    {'id': 'es', 'desc': 'Español', 'country': 'ec'}
]
locale_tuples = [(loc['id'], loc['country'], loc['desc']) for loc in locale_data]

key_data = [
    {'id': 'app.name', 'desc': 'Application name'},
    {'id': 'courses.name', 'desc': 'Name of the courses module'},
    {'id': 'btn.ok', 'desc': 'Label on an OK button'},
    {'id': 'label.name.first', 'desc': 'Label for a first name prompt'},
    {'id': 'label.name.last', 'desc': 'Label for a last name prompt'}
]
key_tuples = [(val['id'], val['desc']) for val in key_data]


def create_locales(dbs):
    dbs.add_all([I18NLocale(**d) for d in locale_data])
    dbs.commit()


def create_keys(dbs):
    dbs.add_all([I18NKey(**k) for k in key_data])
    dbs.commit()


def create_values(dbs):
    for locale in locale_data:
        for key in key_data:
            val = I18NValue(locale_id=locale['id'],
                            key_id=key['id'],
                            gloss=f"{key['desc']} in {locale['desc']}")
            dbs.add(val)
    dbs.commit()


def seed_database(dbs):
    """Utility function for seeding empty database."""
    create_locales(dbs)
    create_keys(dbs)
    create_values(dbs)


# ---- Locales

def test_read_all_locales(client, dbs):
    # GIVEN locales from static data
    create_locales(dbs)

    # WHEN we request all locales
    resp = client.get(url_for('i18n.read_all_locales'))

    # THEN result is "Ok" and we get back the same number of locales.
    assert resp.status_code == 200
    assert len(resp.json) == len(locale_data)
    for locale in resp.json:
        assert locale['id']
        assert locale['desc']
        assert locale['country']


@pytest.mark.parametrize('id, country, desc', locale_tuples)
def test_read_one_locale(client, dbs, id, country, desc):
    # GIVEN locales from static data
    create_locales(dbs)

    # WHEN we read one of them
    resp = client.get(url_for('i18n.read_one_locale', locale_id=id))

    # THEN result is "Ok" and we get back the expected locale
    assert resp.status_code == 200
    assert resp.json['id'] == id
    assert resp.json['country'] == country
    assert resp.json['desc'] == desc


@pytest.mark.parametrize('id', ['', 'a', 'aa', 'aaa', 'aa-aa'])
def test_read_nonexistent_locale(client, id):
    # GIVEN any set of locales
    # WHEN we try to fetch a locale with a bogus name
    resp = client.get(url_for('i18n.read_one_locale', locale_id=id))
    # THEN result is "Not fount"
    assert resp.status_code == 404


@pytest.mark.parametrize('id', ['', 'a', 'a-', '-a', 'aa-', 'aaa-', 'aa-a'])
def test_create_bogus_locale(client, id):
    # GIVEN any set of locales
    # WHEN we try to create one with a bogus ID
    resp = client.post(url_for('i18n.create_locale'),
                       json={'id': id, 'desc': id * 2})
    # THEN result is "Unprocessable"
    assert resp.status_code == 422


@pytest.mark.usefixtures('orm')
@pytest.mark.parametrize('id, country, desc', locale_tuples)
def test_create_valid_locale(client, id, country, desc):
    # GIVEN empty locale table
    # WHEN one local added
    resp = client.post(url_for('i18n.create_locale'),
                       json={'id': id, 'country': country, 'desc': desc})

    # THEN result is "Created"
    assert resp.status_code == 201

    # AND there is one local in the DB and it matches the one created.
    result = I18NLocale().query.all()
    assert len(result) == 1
    assert result[0].id == id
    assert result[0].desc == desc


@pytest.mark.parametrize('id, country, desc', locale_tuples)
def test_delete_one_locale(client, dbs, id, country, desc):
    # GIVEN locales from static data
    create_locales(dbs)

    # WHEN one locale deleted
    resp = client.delete(url_for('i18n.delete_one_locale', locale_id=id))

    # THEN result is "No content"
    assert resp.status_code == 204

    # AND the deleted locale doesn't exist in the database.
    result = I18NLocale().query.all()
    assert len(result) == len(locale_tuples) - 1
    for loc in result:
        assert loc.id != id
        assert loc.desc != desc
        assert loc.country != country


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
    assert resp.status_code == 201


# ---- Values

def test_read_all_values(client, dbs):
    create_values(dbs)
    resp = client.get(url_for('i18n.read_all_values'))
    assert resp.status_code == 200
    assert len(resp.json) == len(locale_data) * len(key_data)
