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
    tokens_data = database.token.new_survey.paginate(page=page, per_page=10)
    page_data = {
        'title': 'Manage Surveys - Itinerum Control Panel',
        'new_survey_tokens': tokens_data
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

