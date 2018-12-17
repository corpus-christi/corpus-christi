import os
from collections import defaultdict
from functools import reduce

import pytest
from flask import url_for, json

from src.i18n.models import I18NLocale, I18NKey, I18NValue, I18NCountryCode, I18NLanguageCode

locale_data = [
    {'id': 'en', 'desc': 'English', 'country': 'us'},
    {'id': 'es', 'desc': 'Español', 'country': 'ec'}
]
locale_tuples = [(loc['id'], loc['country'], loc['desc']) for loc in locale_data]
locale_ids = [loc['id'] for loc in locale_data]

key_data = [
    {'id': 'alt.logo', 'desc': 'Alt text for logo'},
    {'id': 'app.name', 'desc': 'Application name'},
    {'id': 'app.desc', 'desc': 'This is a test application'},
    {'id': 'courses.name', 'desc': 'Name of the courses module'},
    {'id': 'courses.date.start', 'desc': 'Start date of course'},
    {'id': 'courses.date.end', 'desc': 'End date of course'},
    {'id': 'btn.ok', 'desc': 'Label on an OK button'},
    {'id': 'btn.cancel', 'desc': 'Label on a Cancel button'},
    {'id': 'label.name.first', 'desc': 'Label for a first name prompt'},
    {'id': 'label.name.last', 'desc': 'Label for a last name prompt'}
]
key_tuples = [(val['id'], val['desc']) for val in key_data]


def count_unique_top_level_ids(key_data_list):
    """Count the number of top-level keys that should result from
    converting key_data to a nested tree structure.
    """
    unique = defaultdict(int)
    for id in (key['id'] for key in key_data_list):
        unique[id.split('.')[0]] += 1
    print("UNIQUE", unique)
    return len(unique)


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


def data_file_path(file_name):
    rtn = os.path.join(__file__, os.path.pardir, 'data', file_name)
    return os.path.abspath(rtn)


def load_country_codes(orm):
    data = None
    with open(data_file_path('country-codes.json'), 'r') as fp:
        data = json.load(fp)

    objs = [I18NCountryCode(code=code['Code'], name=code['Name']) for code in data]
    orm.add_all(objs)
    orm.commit()
    return len(objs)


def load_language_codes(orm):
    data = None
    with open(data_file_path('language-codes.json'), 'r') as fp:
        data = json.load(fp)

    objs = [I18NLanguageCode(code=code['alpha2'], name=code['English']) for code in data]
    orm.add_all(objs)
    orm.commit()
    return len(objs)


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


@pytest.mark.parametrize('format', [None, 'list'])
@pytest.mark.parametrize('id', locale_ids)
def test_one_locale_as_list(client, format, dbs, id):
    if format is None:
        # Default format
        url = url_for('i18n.read_xlation', locale_id=id)
    elif format == 'list':
        # Format `list`
        url = url_for('i18n.read_xlation', locale_id=id, format=format)
    else:
        # Something went terribly wrong.
        assert False

    # GIVEN i18n test data
    seed_database(dbs)
    # WHEN asking for translations for a given locale
    resp = client.get(url)
    # THEN response should be "Ok"
    assert resp.status_code == 200
    # AND there should be as many rows as there are keys.
    assert len(resp.json) == len(key_data)


def count_leaf_nodes(node):
    """Count the number of leaf nodes in a tree of nested dictionaries."""
    if not isinstance(node, dict):
        return 1
    else:
        return reduce(lambda x, y: x + y,
                      [count_leaf_nodes(node) for node in node.values()], 0)


@pytest.mark.parametrize('id', locale_ids)
def test_one_locale_as_tree(client, dbs, id):
    # GIVEN i18n test data
    seed_database(dbs)
    # WHEN asking for a tree of translation information
    resp = client.get(url_for('i18n.read_xlation', locale_id=id, format='tree'))
    # THEN response should be 'Ok'
    assert resp.status_code == 200
    # AND tree should have proper number of top-level entries
    assert len(resp.json) == count_unique_top_level_ids(key_data)
    # AND should have the proper number of leaf nodes
    assert count_leaf_nodes(resp.json) == len(key_data)
    # AND should have values in nested dictionaries.
    assert resp.json['label']['name']['first'].startswith('Label for a first')


# ---- Languages and countries

@pytest.mark.parametrize('code, name', [('US', 'United States'),
                                        ('EC', 'Ecuador'),
                                        ('TH', 'Thailand')])
def test_read_country(client, dbs, code, name):
    load_country_codes(dbs)
    resp = client.get(url_for('i18n.read_countries', country_code=code))
    assert resp.status_code == 200
    assert resp.json['name'] == name


def test_read_all_countries(client, dbs):
    count = load_country_codes(dbs)
    resp = client.get(url_for('i18n.read_countries'))
    assert resp.status_code == 200
    assert len(resp.json) == count


@pytest.mark.parametrize('code, name', [('en', 'English'),
                                        ('th', 'Thai'),
                                        ('es', 'Spanish; Castilian')])
def test_read_language(client, dbs, code, name):
    load_language_codes(dbs)
    resp = client.get(url_for('i18n.read_languages', language_code=code))
    print("RESP", resp.json)
    assert resp.status_code == 200
    assert resp.json['name'] == name

def test_read_all_languages(client, dbs):
    count = load_language_codes(dbs)
    resp = client.get(url_for('i18n.read_languages'))
    assert resp.status_code == 200
    assert len(resp.json) == count
