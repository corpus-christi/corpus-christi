import pytest
from flask import url_for

from .auth.utils import jwt_not_required


@pytest.mark.smoke
@jwt_not_required
def test_ping(plain_client):
    resp = plain_client.get(url_for('etc.ping'))
    assert resp.status_code == 200
    assert resp.json['ping'] == 'pong'
