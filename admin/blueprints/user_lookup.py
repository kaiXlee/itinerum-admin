#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2018
from flask import Blueprint, render_template, request

from admin.database import Database
from utils.basic_auth import requires_auth


blueprint = Blueprint('user_lookup', __name__)
database = Database()


@blueprint.route('/', methods=['GET', 'POST'])
@requires_auth
def index():
    if request.method == 'GET':
        response = {
            'title': 'User Lookup - Itinerum Control Panel',
            'surveys': database.survey_admin.names()
        }
        return render_template('user_lookup.index.html', **response)
    elif request.method == 'POST':
        uuid_or_email = request.form.get('uuidOrEmail', '').strip()
        survey_name = request.form.get('surveyName', '').strip()
        page = int(request.form.get('pageNum', 1))

        if uuid_or_email:
            users = database.user_lookup.paginate(survey_name=survey_name,
                                                  page=page,
                                                  uuid_or_email=uuid_or_email)
        else:
            users = database.user_lookup.paginate(survey_name=survey_name, page=page)

        response = {
            'users': [],
            'pages': users.pages,
            'per_page': users.per_page
        }
        for user in users.items:
            # format timestamps in Montreal local time
            created_at = user.created_at.astimezone(server_tz).strftime('%Y-%m-%d %H:%M:%S')
            last_mobile_update = None
            if user.last_coordinate:
                last_mobile_update = (user.last_coordinate.timestamp
                                                          .astimezone(server_tz)
                                                          .strftime('%Y-%m-%d %H:%M:%S'))
            response['users'].append({
                'id': user.id,
                'created_at': created_at,
                'email': user.email,
                'last_coordinate': last_mobile_update,
                'survey_administrator': user.admin_user.email,
                'survey_language': user.survey.language,
                'survey': user.survey.pretty_name,
                'survey_id': user.survey_id,
                'uuid': user.uuid
            })
        return make_response(jsonify(response))
