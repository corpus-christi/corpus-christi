import datetime
import random
import pytest
from flask import url_for


def test_create_error_report(auth_client):
    # GIVEN an empty database
    # WHEN we create a number of error reports
    count = random.randint(5, 15)
    resp = auth_client.post(
        url_for('error_report.create_error_report'),
        json={
            'description': '404 eror found',
            'status_code': '404',
            'endpoint': 'groups/group/1',
            'solved': 0,
            'time_stamp': '2020-05-01 12:12:12'
        })
    print(url_for('error_report.create_error_report'))
    assert resp.status_code == 201
