#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017
import base64
import json

from admin.tests.fixtures import *
from admin.database import Database

database = Database()
valid_credentials = base64.b64encode(b'admin:admin').decode('utf-8')


# generates a new survey registration token
def test_generate_survey_registration_token_success(client):
    body = {}
    r = client.post('/new-survey/token',
                    data=json.dumps(body),
                    headers={'Authorization': 'Basic ' + valid_credentials},
                    content_type='application/json')
    response = json.loads(r.data)
    assert r.status_code == 201
    assert response['status'] == 'success'
    new_token = response['results']['recent_tokens'][0]
    assert bool(new_token['active']) is True

    db_result = database.token.new_survey.get_recent(1).first()
    assert db_result.token == new_token['token']
