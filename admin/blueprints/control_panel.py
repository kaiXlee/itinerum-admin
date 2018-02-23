#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
import codecs
import csv
from datetime import date, datetime, timedelta
from flask import (Blueprint, current_app, jsonify, make_response,
                   render_template, request, Response)
import io
import json
import os
import pytz
import time

from admin.database import Database
from utils.basic_auth import requires_auth
from utils.responses import Success, Error


blueprint = Blueprint('control_panel', __name__)
database = Database()
server_tz = pytz.timezone('America/Montreal')


@blueprint.route('/')
@requires_auth
def index():
    page_data = {
        'title': 'Overview - Itinerum Control Panel',
        'surveys': database.survey_admin.names()
    }
    page_data.update(database.token.counts())
    return render_template('control_panel.index.html', **page_data)


@blueprint.route('/health')
def ecs_health_check():
    response = {'status': 0}
    return make_response(jsonify(response))


@blueprint.route('/export')
@requires_auth
def export_csv():
    survey = request.args.get('survey')
    yesterday = date.today() - timedelta(days=1)
    start = yesterday.strftime('%Y-%m-%d 00:00:00')
    start_dt = datetime.strptime(start, '%Y-%m-%d %H:%M:%S').replace(tzinfo=server_tz)
    end = yesterday.strftime('%Y-%m-%d 23:59:59')
    end_dt = datetime.strptime(end, '%Y-%m-%d %H:%M:%S').replace(tzinfo=server_tz)

    summary = database.survey_admin.generate_summary(survey_name=survey,
                                                     start=start_dt,
                                                     end=end_dt)

    summary_rows = [
        [survey.encode('utf-8')],
        [yesterday.strftime('%d-%m-%Y')],
        [],
        ['New users', 'Active users', 'Points', 'Prompts'],
        [summary['new_users'], summary['active_users'], summary['num_points'], summary['num_prompts']]
    ]

    filestream = io.BytesIO()
    filestream.write(codecs.BOM_UTF8)
    writer = csv.writer(filestream)
    writer.writerows(summary_rows)
    csv_data = filestream.getvalue().strip('\r\n')

    csv_fn = '{survey}-{date}.csv'.format(survey=survey.encode('utf-8'), date=yesterday)
    headers = {
        'Content-disposition': 'attachment; filename={fn}'.format(fn=csv_fn)
    }
    response = Response(csv_data,
                        mimetype='text/csv',
                        headers=headers)
    response.content_type = 'text/csv'
    return response


@blueprint.route('/logout')
def logout():
    message = 'You have successfully logged out. Click <a href="./">here</a> to return.'
    return Response(message, 401)
