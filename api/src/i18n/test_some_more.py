from src.models import I18NLocale

BASE_URL = 'http://localhost:5000/api/v1/i18n'


# def test_sample(session):
#     locale = I18NLocale(id="de", desc="Deutsch")
#     session.add(locale)
#     session.commit()
#
#
# @pytest.mark.parametrize('id,desc', [('su', 'Finnish')])
# def test_create_valid_locale(id, desc):
#     resp = requests.post(f'{BASE_URL}/locales', json={'id': id, 'desc': desc})
#     assert resp.status_code == 200


def test_app_connection(app):
    assert app.name == 'src'


def test_ping(client):
    resp = client.get('/ping')
    assert resp.data == b'pong'


def test_sample(client, session):
    locale = I18NLocale(id="de", desc="Deutsch")
    print("LOCALE", locale)
    session.add(locale)
    session.commit()

    resp = client.get(f'{BASE_URL}/locales')
    json = resp.get_json()
    print("JSON", json)
    assert json[0]['desc'] == 'Deutsch'


# def test_read_all_locales(client):
#     resp = client.get(f'{BASE_URL}/locales')
#     assert resp.status_code == 200
#     json = resp.json()
#     assert len(json) == 3
