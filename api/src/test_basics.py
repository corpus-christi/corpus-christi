import pytest
from flask import url_for


@pytest.mark.smoke
def test_ping(plain_client):
    resp = plain_client.get(url_for('etc.ping'))
    assert resp.status_code == 200
    assert resp.json['ping'] == 'pong'
