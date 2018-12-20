from collections import defaultdict
from functools import reduce

import pytest
from flask import url_for

from src import db
from src.i18n.models import I18NLocale, I18NKey, I18NValue, Language, i18n_read, i18n_update, i18n_delete, i18n_check

locale_data = [
    {'code': 'en-US', 'desc': 'English US'},
    {'code': 'es-EC', 'desc': 'Español Ecuador'},
    {'code': 'en-GB', 'desc': 'English GB'}
]
locale_tuples = [(loc['code'], loc['desc']) for loc in locale_data]
locale_codes = [loc['code'] for loc in locale_data]

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
    return len(unique)


def create_locales(db):
    db.session.add_all([I18NLocale(**d) for d in locale_data])
    db.session.commit()


def create_keys(db):
    db.session.add_all([I18NKey(**k) for k in key_data])
    db.session.commit()


def create_values(db):
    for locale in locale_data:
        for key in key_data:
            val = I18NValue(locale_code=locale['code'],
                            key_id=key['id'],
                            gloss=f"{key['desc']} in {locale['desc']}")
            db.session.add(val)
    db.session.commit()


def seed_database(db):
    """Utility function for seeding empty database."""
    create_locales(db)
    create_keys(db)
    create_values(db)


# ---- Locales

def test_read_all_locales(client, db):
    # GIVEN locales from static data
    create_locales(db)

    # WHEN we request all locales
    resp = client.get(url_for('i18n.read_all_locales'))

    # THEN result is "Ok" and we get back the same number of locales.
    assert resp.status_code == 200
    assert len(resp.json) == len(locale_data)
    for locale in resp.json:
        assert locale['code']
        assert locale['desc']


@pytest.mark.parametrize('code, desc', locale_tuples)
def test_read_one_locale(client, db, code, desc):
    # GIVEN locales from static data
    create_locales(db)

    # WHEN we read one of them
    resp = client.get(url_for('i18n.read_one_locale', locale_code=code))

    # THEN result is "Ok" and we get back the expected locale
    assert resp.status_code == 200
    assert resp.json['code'] == code
    assert resp.json['desc'] == desc


@pytest.mark.parametrize('code', ['', 'a', 'aa', 'aaa', 'aa-aa'])
def test_read_nonexistent_locale(client, code):
    # GIVEN any set of locales
    # WHEN we try to fetch a locale with a bogus name
    resp = client.get(url_for('i18n.read_one_locale', locale_code=code))
    # THEN result is "Not fount"
    assert resp.status_code == 404


@pytest.mark.parametrize('code', ['', 'a', 'a-', '-a', 'aa', 'aa-', 'aa-a'])
def test_create_bogus_locale(client, code):
    # GIVEN any set of locales
    # WHEN we try to create one with a bogus code
    resp = client.post(url_for('i18n.create_locale'),
                       json={'code': code, 'desc': code * 2})
    # THEN result is "Unprocessable"
    assert resp.status_code == 422


@pytest.mark.usefixtures('reset_db')
@pytest.mark.parametrize('code, desc', locale_tuples)
def test_create_valid_locale(client, code, desc):
    # GIVEN empty locale table
    # WHEN one local added
    resp = client.post(url_for('i18n.create_locale'), json={'code': code, 'desc': desc})

    # THEN result is "Created"
    assert resp.status_code == 201

    # AND there is one local in the DB and it matches the one created.
    result = db.session.query(I18NLocale).all()
    assert len(result) == 1
    assert result[0].code == code
    assert result[0].desc == desc


@pytest.mark.parametrize('code, desc', locale_tuples)
def test_delete_one_locale(client, db, code, desc):
    # GIVEN locales from static data
    create_locales(db)

    # WHEN one locale deleted
    resp = client.delete(url_for('i18n.delete_one_locale', locale_code=code))

    # THEN result is "No content"
    assert resp.status_code == 204

    # AND the deleted locale doesn't exist in the database.
    result = db.session.query(I18NLocale).all()
    assert len(result) == len(locale_tuples) - 1
    for loc in result:
        assert loc.code != code
        assert loc.desc != desc


# ---- Keys

def test_read_all_keys(client, db):
    create_keys(db)
    resp = client.get(url_for('i18n.read_all_keys'))
    assert resp.status_code == 200
    assert len(resp.json) == len(key_data)


@pytest.mark.parametrize('id, desc', key_tuples)
def test_read_existing_key(client, db, id, desc):
    create_keys(db)
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


@pytest.mark.usefixtures('reset_db')
@pytest.mark.parametrize('id,desc', key_tuples)
def test_create_valid_key(client, id, desc):
    resp = client.post(url_for('i18n.create_key'),
                       json={'id': id, 'desc': desc})
    assert resp.status_code == 201


# ---- Values

def test_read_all_values(client, db):
    create_values(db)
    resp = client.get(url_for('i18n.read_all_values'))
    assert resp.status_code == 200
    assert len(resp.json) == len(locale_data) * len(key_data)


@pytest.mark.parametrize('format', [None, 'list'])
@pytest.mark.parametrize('code', locale_codes)
def test_one_locale_as_list(client, format, db, code):
    if format is None:
        # Default format
        url = url_for('i18n.read_xlation', locale_code=code)
    elif format == 'list':
        # Format `list`
        url = url_for('i18n.read_xlation', locale_code=code, format=format)

    # GIVEN i18n test data
    seed_database(db)
    # WHEN asking for translations for a given locale
    resp = client.get(url)
    # THEN response should be "Ok"
    assert resp.status_code == 200
    # AND there should be as many rows as there are keys.
    assert len(resp.json) == len(key_data)


def test_bogus_xlation_locale(client):
    resp = client.get(url_for('i18n.read_xlation', locale_code='not-a-real-locale'))
    assert resp.status_code == 404


def test_bogus_xlation_format(client):
    resp = client.get(url_for('i18n.read_xlation',
                              locale_code=locale_codes[0],
                              format='not-a-valid-format'))
    assert resp.status_code == 400


def test_goofy_tree_structure(client, db):
    # We're about to put this entry in the database
    # {'id': 'btn.cancel', 'desc': 'Label on a Cancel button'},
    seed_database(db)

    # Now add a child of a string, which makes no sense.
    bogus_key_id = 'btn.cancel.bogus'
    db.session.add(I18NKey(id=bogus_key_id, desc='Invalid key'))
    db.session.add(I18NValue(locale_code=locale_data[0]['code'],
                             key_id=bogus_key_id,
                             gloss="Bogus Gloss"))
    db.session.commit()

    # Ask the API for a valid tree. It shouldn't comply.
    resp = client.get(url_for('i18n.read_xlation',
                              locale_code=locale_codes[0],
                              format='tree'))
    assert resp.status_code == 400


def count_leaf_nodes(node):
    """Count the number of leaf nodes in a tree of nested dictionaries."""
    if not isinstance(node, dict):
        return 1
    else:
        return reduce(lambda x, y: x + y,
                      [count_leaf_nodes(node) for node in node.values()], 0)


@pytest.mark.parametrize('code', locale_codes)
def test_one_locale_as_tree(client, db, code):
    # GIVEN i18n test data
    seed_database(db)
    # WHEN asking for a tree of translation information
    resp = client.get(url_for('i18n.read_xlation', locale_code=code, format='tree'))
    # THEN response should be 'Ok'
    assert resp.status_code == 200
    # AND tree should have proper number of top-level entries
    assert len(resp.json) == count_unique_top_level_ids(key_data)
    # AND should have the proper number of leaf nodes
    assert count_leaf_nodes(resp.json) == len(key_data)
    # AND should have values in nested dictionaries.
    assert resp.json['label']['name']['first'].startswith('Label for a first')


# ---- Languages

@pytest.mark.slow
@pytest.mark.parametrize('code, name', [('en', 'English'),
                                        ('th', 'Thai'),
                                        ('es', 'Spanish; Castilian')])
def test_read_language(client, db, code, name):
    count = Language.load_from_file()
    assert count > 0
    resp = client.get(url_for('i18n.read_languages', language_code=code, locale='en-US'))
    assert resp.status_code == 200
    assert resp.json['name'] == name


@pytest.mark.slow
def test_read_all_languages(client, db):
    count = Language.load_from_file()
    assert count > 0
    resp = client.get(url_for('i18n.read_languages', locale='en-US'))
    assert resp.status_code == 200
    assert len(resp.json) == count


# ---- I18N CRUD

def test_good_crud_read(db):
    id = 'foo.bar'
    locale = 'xx-YY'
    gloss = 'Zippy'

    db.session.add_all([
        I18NKey(id=id, desc='Fake Description'),
        I18NValue(key_id=id, locale_code=locale, gloss=gloss)
    ])
    db.session.commit()
    assert i18n_read(id, locale).gloss == gloss


@pytest.mark.usefixtures('reset_db')
def test_bad_crud_read():
    with pytest.raises(RuntimeError):
        i18n_read('bogus', 'bogus')


def test_good_crud_update(db):
    id = 'foo.bar'
    locale = 'xx-YY'
    first_gloss = 'Zippy'
    new_gloss = 'Flippy'

    db.session.add_all([
        I18NKey(id=id, desc='Fake Description'),
        I18NValue(key_id=id, locale_code=locale, gloss=first_gloss)
    ])
    assert i18n_read(id, locale).gloss == first_gloss

    try:
        i18n_update(id, locale, new_gloss)
    except Exception:
        pytest.fail('Expected update to work')
    assert i18n_read(id, locale).gloss == new_gloss


@pytest.mark.usefixtures('reset_db')
def test_bad_crud_update():
    with pytest.raises(RuntimeError):
        i18n_read('bogus', 'bogus')


@pytest.mark.usefixtures('reset_db')
def test_bad_crud_delete():
    with pytest.raises(RuntimeError):
        i18n_read('bogus', 'bogus')


def test_good_crud_delete(db):
    id = 'foo.bar'
    locale = 'xx-YY'
    gloss = 'Zippy'

    db.session.add_all([
        I18NKey(id=id, desc='Fake Description'),
        I18NValue(key_id=id, locale_code=locale, gloss=gloss)
    ])
    assert i18n_read(id, locale).gloss == gloss

    try:
        i18n_delete(id, locale)
    except Exception:
        pytest.fail('Expected delete to work')

    assert i18n_check(id, locale) is None
