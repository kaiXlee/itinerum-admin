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
    registered_surveys_data = database.survey_admin.paginate(page=page, per_page=10)
    page_data = {
        'title': 'Manage Surveys - Itinerum Control Panel',
        'registered_surveys': registered_surveys_data
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
        survey_name = request.json['surveyName']
        error = database.survey_admin.create_from_schema(survey_name=survey_name,
                                                         admin_email=request.json['schema']['adminEmail'],
                                                         admin_password=request.json['schema']['adminPassword'],
                                                         language=request.json['schema']['language'],
                                                         survey_questions=request.json['schema']['surveyQuestions'],
                                                         survey_prompts=request.json['schema']['surveyPrompts'])
        if not error:
            # format the same as jinja2 renders the template
            response = {
                'recent_signups': [],
                'message': 'Survey "{}" created.'.format(survey_name)
            }            
            for survey in database.survey_admin.get_recent_signups(10):
                response['recent_signups'].append({
                    'name': survey.name,
                    'pretty_name': survey.pretty_name,
                    'created_at': str(survey.created_at.replace(microsecond=0)),
                    'active': 'True' if survey.mobile_coordinates.one_or_none() else 'False'
                })

            return Success(status_code=201,
                           headers={'Location': '/manage-surveys/schema'},
                           resource_type='NewSurveySchema',
                           body=response)
        errors = [error]

    if not errors:
        errors = ['New survey schema could not be uploaded.']
    return Error(status_code=400,
                 headers={'Location': '/manage-surveys/schema'},
                 resource_type='NewSurveySchema',
                 errors=errors)


@blueprint.route('/delete', methods=['DELETE'])
@requires_auth
def delete_inactive_survey():
    survey_name = request.form.get('surveyName')
    error = database.survey_admin.delete(survey_name)
    if not error:
        # format the same as jinja2 renders the template
        response = {
            'recent_signups': [],
            'message': 'Survey "{}" deleted.'.format(survey_name)
        }

        for survey in database.survey_admin.get_recent_signups(10):
            response['recent_signups'].append({
                'name': survey.name,
                'pretty_name': survey.pretty_name,
                'created_at': str(survey.created_at.replace(microsecond=0)),
                'active': 'True' if survey.mobile_coordinates.one_or_none() else 'False'
            })

        return Success(status_code=200,
                       headers={'Location': '/manage-surveys/delete'},
                       resource_type='NewSurveySchema',
                       body=response)
    return Error(status_code=400,
                 headers={'Location': '/manage-surveys/delete'},
                 resource_type='NewSurveySchema',
                 errors=[error])




