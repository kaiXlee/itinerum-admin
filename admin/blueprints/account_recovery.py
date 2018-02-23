#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2018
from flask import Blueprint, render_template, request

from admin.database import Database
from utils.basic_auth import requires_auth
from utils.responses import Success, Error


blueprint = Blueprint('account_recovery', __name__)
database = Database()


@blueprint.route('/', methods=['GET', 'POST'])
@requires_auth
def index():
    if request.method == 'GET':
        response = {'title': 'Account Recovery Tokens - Itinerum Control Panel'}
        return render_template('account_recovery.index.html', **response)
    elif request.method == 'POST':
        page = int(request.form.get('pageNum', 1))
        email = request.form.get('email', '').strip()
        tokens = database.token.account_recovery.latest(email=email)

        pagination = tokens.paginate(page=page, per_page=10)
        response = {
            'latest_tokens': [],
            'pages': pagination.pages,
            'per_page': pagination.per_page
        }
        for token in pagination.items:
            used_at = None
            if not token.active:
                used_at = (token.modified_at.astimezone(server_tz)
                                            .replace(microsecond=0)
                                            .strftime('%Y-%m-%d %H:%M:%S'))
            response['latest_tokens'].append({
                'id': token.id,
                'survey_id': token.web_user.survey_id,
                'pretty_name': token.web_user.survey.pretty_name,
                'email': token.web_user.email,
                'token': token.token,
                'used_at': used_at
            })
        return make_response(jsonify(response))


@blueprint.route('/deactivate', methods=['POST'])
@requires_auth
def disable_account_recovery_token():
    token_id = request.form['tokenId']
    token = database.token.account_recovery.disable(token_id)
    response = {
        'message': 'WebUserResetPasswordToken {id} disabled.'.format(id=token.id)
    }
    return Success(status_code=201,
                   headers={'Location': '/account-recovery/deactivate'},
                   resource_type='DeactivateNewSurveyToken',
                   body=response)
