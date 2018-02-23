#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2018
from flask import Blueprint, render_template, request

from admin.database import Database
from utils.basic_auth import requires_auth
from utils.responses import Success, Error


blueprint = Blueprint('signup_tokens', __name__)
database = Database()


@blueprint.route('/')
@requires_auth
def index():
    page = int(request.args.get('page', 1))
    tokens_data = database.token.new_survey.paginate(page=page, per_page=10)
    page_data = {
        'title': 'Survey Sign-Up Tokens - Itinerum Control Panel',
        'new_survey_tokens': tokens_data
    }
    return render_template('signup_tokens.index.html', **page_data)


@blueprint.route('/token', methods=['POST'])
@requires_auth
def generate_new_survey_token():
    database.token.new_survey.create()
    response = {
        'recent_tokens': [],
        'message': 'New survey sign-up token successfully created.'
    }

    # format the same as jinja2 renders the template
    for token in database.token.new_survey.get_recent(10):
        response['recent_tokens'].append({
            'token': token.token,
            'created_at': token.created_at,
            'active': str(token.active),
            'usages': token.usages
        })

    return Success(status_code=201,
                   headers={'Location': '/signup-tokens/token'},
                   resource_type='NewSurveyToken',
                   body=response)

