import pytest
import requests

def test_get_locales():
    resp = requests.get('http://localhost:5000/api/v1/i18n/locales')
    assert resp.status_code == 200
    json = resp.json()
    assert len(json) == 2

