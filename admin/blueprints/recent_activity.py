#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
from flask import Blueprint, jsonify, make_response, render_template, request
from datetime import datetime, timedelta
import pytz

from admin.database import Database
from utils.basic_auth import requires_auth
from utils.responses import Success, Error

blueprint = Blueprint('recent_activity', __name__)
database = Database()


@blueprint.route('/', methods=['GET'])
@requires_auth
def index():
    response = {}
    return render_template('recent_activity.index.html', **response)


@blueprint.route('/data', methods=['POST'])
@requires_auth
def recent_activity():
    start = datetime.now(pytz.utc) - timedelta(hours=1)
    end = datetime.now(pytz.utc)

    points_feature = {
        'type': 'MultiPoint',
        'coordinates': [],
        'properties': {
            'timestamps': [],
            'mobile_ids': []
        }
    }

    newest = 0
    oldest = 999999999999999
    for c in database.activity.coordinates_by_times(start, end):
        points_feature['coordinates'].append([float(c.longitude), float(c.latitude)])
        ts = int(time.mktime(c.timestamp.utctimetuple()))
        points_feature['properties']['timestamps'].append(ts)
        points_feature['properties']['mobile_ids'].append(c.mobile_id)

        if ts > newest:
            newest = ts
        if ts < oldest:
            oldest = ts
    points_feature['properties']['start'] = oldest
    points_feature['properties']['end'] = newest

    # prompts_feature = {
    #     'type': 'Feature',
    #     'geometry': {
    #         'type': 'MultiPoint',
    #         'coordinates': []
    #     },
    #     'properties': {'type': 'prompts'}
    # }
    # for c in database.activity.prompts_by_times(start, end):
    #     prompts_feature['geometry']['coordinates'].append([float(c.longitude), float(c.latitude)])

    # response = {
    #     'geojson': {
    #         'type': 'FeatureCollection',
    #         'features': [points_feature]
    #     }
    # }

    return make_response(jsonify(points_feature))


@blueprint.route('/data/<mobile_id>', methods=['POST'])
@requires_auth
def recent_user_activity(mobile_id):
    points_feature = {
        'type': 'MultiPoint',
        'coordinates': [],
        'properties': {
            'uuid': None,
            'survey_id': None,
            'survey_name': None,
            'timestamps': [],
            'start': None,
            'end': None
        }
    }

    user = database.user_lookup.get(mobile_id)
    survey = user.survey_response.one_or_none()
    if user:
        points_feature['properties']['uuid'] = user.uuid
        points_feature['properties']['survey_id'] = user.survey_id
        points_feature['properties']['survey_name'] = user.survey.pretty_name

        if survey:
            points_feature['properties']['email'] = survey.response.get('Email')

        points = database.activity.coordinates_by_mobile_id(mobile_id)
        for p in points:
            ts = int(time.mktime(p.timestamp.utctimetuple()))
            points_feature['properties']['timestamps'].append(ts)
            points_feature['coordinates'].append([float(p.longitude), float(p.latitude)])

    points_feature['properties']['start'] = points_feature['properties']['timestamps'][0]
    points_feature['properties']['end'] = points_feature['properties']['timestamps'][-1]
    return make_response(jsonify(points_feature))

@blueprint.route('/export', methods=['GET'])
@requires_auth
def recent_user_activity_geojson():
    mobile_id = request.args.get('mobileuser')
    user_geojson = {
        'type': 'FeatureCollection',
        'features': []
    }

    points = database.activity.coordinates_by_mobile_id(mobile_id)
    for p in points:
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [float(p.longitude), float(p.latitude)]
            },
            'properties': {
                'id': p.id,
                'timestamp': p.timestamp.isoformat(),
                'h_accuracy': float(p.h_accuracy),
                'v_accuracy': float(p.v_accuracy),
                'speed': float(p.speed)

            }
        }
        user_geojson['features'].append(feature)
    return Response(json.dumps(user_geojson, indent=4),
                    mimetype='text/json',
                    headers={'Content-disposition': 'attachment; filename=mobileid-{}.geojson'.format(mobile_id)})