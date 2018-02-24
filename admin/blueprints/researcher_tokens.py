#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2018
from flask import Blueprint, render_template, request

from admin.database import Database
from utils.basic_auth import requires_auth
from utils.responses import Success, Error


blueprint = Blueprint('researcher_tokens', __name__)
database = Database()


@blueprint.route('/')
@requires_auth
def index():
    page_data = {
        'title': 'Researcher Invite Tokens - Itinerum Control Panel',
        'researcher_tokens': []
    }
    for token in database.token.researcher_invite.get_active():
        page_data['researcher_tokens'].append({
            'token': token.token,
            'survey_id': token.survey_id,
            'pretty_name': token.survey.pretty_name,
            'admin_email': database.survey_admin.get_admin_email(token.survey),
            'created_at': token.created_at.replace(microsecond=0),
            'usages': token.usages
        })

    return render_template('researcher_tokens.index.html', **page_data)

