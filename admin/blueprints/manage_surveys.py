#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2018
from flask import Blueprint, render_template, request

from admin.database import Database
from utils.basic_auth import requires_auth
from utils.responses import Success, Error


blueprint = Blueprint('manage_surveys', __name__)
database = Database()


@blueprint.route('/')
@requires_auth
def index():
    page = int(request.args.get('page', 1))
    pagination_data = database.token.new_survey.paginate(page=page, per_page=10)
    print(pagination_data.prev_num)
    page_data = {
        'title': 'Manage Surveys - Itinerum Control Panel',
        'new_survey_tokens': pagination_data,
        'new_survey_tokens_page': pagination_data.page,
        'new_survey_tokens_pages': pagination_data.pages,
        'new_survey_tokens_total': int(pagination_data.total)
    }
    return render_template('manage_surveys.index.html', **page_data)


@blueprint.route('/schema', methods=['POST'])
@requires_auth
def upload_survey_schema_json():
    if not request.json.get('surveyName'):
        return Error(status_code=400,
                     headers={'Location': '/manage-surveys/schema'},
                     resource_type='NewSurveySchema',
                     errors=['A unique survey name must be provided.'])
    errors = None
    if request.json.get('schema'):
        error = database.survey_admin.create_from_schema(survey_name=request.json['surveyName'],
                                                         admin_email=request.json['schema']['adminEmail'],
                                                         admin_password=request.json['schema']['adminPassword'],
                                                         language=request.json['schema']['language'],
                                                         survey_questions=request.json['schema']['surveyQuestions'],
                                                         survey_prompts=request.json['schema']['surveyPrompts'])
        if not error:
            return Success(status_code=201,
                           headers={'Location': '/manage-surveys/schema'},
                           resource_type='NewSurveySchema',
                           body={})
        errors = [error]

    if not errors:
        errors = ['New survey schema could not be uploaded.']
    return Error(status_code=400,
                 headers={'Location': '/manage-surveys/schema'},
                 resource_type='NewSurveySchema',
                 errors=errors)


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
            'created_at': token.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'active': str(token.active),
            'usages': token.usages
        })

    return Success(status_code=201,
                   headers={'Location': '/manage-surveys/token'},
                   resource_type='NewSurveyToken',
                   body=response)
