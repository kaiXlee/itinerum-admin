#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
from models import MobileCoordinate, MobileUser, Survey, SurveyResponse, WebUser, WebUserRole


class UserLookupActions:
    @staticmethod
    def _append_user_info_queries(user):
        survey_answers = user.survey_response.one_or_none()
        user.email = survey_answers.response.get('Email') if survey_answers else None

        user.last_coordinate = (user.mobile_coordinates.order_by(MobileCoordinate.timestamp.desc())
                                                       .first())
        admin_role = WebUserRole.query.filter_by(name='admin').one()
        user.admin_user = user.survey.web_users.filter(WebUser.roles.contains(admin_role)).one()
        return user

    def _filter_by_survey(self, query, survey_name):
        survey = Survey.query.filter_by(name=survey_name.lower()).one_or_none()
        if survey:
            return query.filter(MobileUser.survey_id == survey.id)
        else:
            return query

    def get(self, mobile_id):
        return MobileUser.query.get(mobile_id)

    def find(self, email_or_uuid, survey_name=None, limit=None):
        query = (MobileUser.query.join(SurveyResponse, MobileUser.survey_response)
                                 .filter(SurveyResponse.response['Email'].astext.ilike(email_or_uuid + '%'))
                                 .order_by(SurveyResponse.response['Email']))

        # lookup as uuid if email not found
        if not query.first():
            query = (MobileUser.query.filter(MobileUser.uuid.ilike(email_or_uuid + '%'))
                                     .order_by(MobileUser.uuid))

        if survey_name:
            query = self._filter_by_survey(query, survey_name)

        users = [self._append_user_info_queries(user) for user in query.limit(limit)]
        return users

    def paginate(self, page=1, survey_name=None, uuid_or_email=None):
        query = (MobileUser.query.join(SurveyResponse, MobileUser.survey_response)
                                 .order_by(SurveyResponse.response['Email']))
        if survey_name:
            query = self._filter_by_survey(query, survey_name)

        if uuid_or_email:
            query = query.filter(SurveyResponse.response['Email'].astext.ilike(uuid_or_email + '%'))
            # lookup as uuid if email not found
            if not query.first():
                query = (MobileUser.query.filter(MobileUser.uuid.ilike(uuid_or_email + '%'))
                                         .order_by(MobileUser.uuid))

        paginated_query = query.paginate(page, per_page=10, error_out=False)
        users_with_info = [self._append_user_info_queries(user) for user in paginated_query.items]
        paginated_query.items = users_with_info
        return paginated_query
