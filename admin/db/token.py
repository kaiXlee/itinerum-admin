#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
from models import db, NewSurveyToken, ResearcherInviteToken, Survey, WebUser, WebUserResetPasswordToken
import uuid


class TokenActions:
    def __init__(self):
        self.new_survey = NewSurveyTokenActions()
        self.researcher_invite = ResearcherInviteTokenActions()
        self.account_recovery = AccountRecoveryTokenActions()

    def counts(self):
        issued = {
            'new_survey': NewSurveyToken.query.count(),
            'researcher_invite': ResearcherInviteToken.query.filter_by(active=True).count(),
            'password_reset': WebUserResetPasswordToken.query.filter_by(active=True).count()
        }
        return issued


class NewSurveyTokenActions:
    def get_active(self):
        return NewSurveyToken.query.filter_by(active=True).one_or_none()

    def get_recent(self, num):
        query = (NewSurveyToken.query
                 .order_by(NewSurveyToken.created_at.desc())
                 .limit(num))
        return query

    def paginate(self, page=0, per_page=10):
        return (NewSurveyToken.query.order_by(NewSurveyToken.created_at.desc())
                                    .paginate(page, per_page))

    def create(self):
        active_token = self.get_active()
        if active_token:
            active_token.active = False

        token = NewSurveyToken(token=uuid.uuid4().hex[:14], active=True)
        db.session.add(token)
        db.session.commit()


class ResearcherInviteTokenActions:
    def get_active(self):
        query = (ResearcherInviteToken.query
                 .order_by(ResearcherInviteToken.created_at.desc())
                 .filter_by(active=True))
        return query


class AccountRecoveryTokenActions:
    def get_recent(self, num):
        query = (WebUserResetPasswordToken.query
                 .order_by(WebUserResetPasswordToken.created_at.desc())
                 .limit(num))
        return query

    def latest(self, page=1, email=None):
        subquery = (db.session.query(WebUserResetPasswordToken.web_user_id,
                                     db.func.max(WebUserResetPasswordToken.created_at).label('latest'))
                              .group_by(WebUserResetPasswordToken.web_user_id)
                              .subquery())

        query = (db.session.query(WebUserResetPasswordToken)
                           .join(WebUser, WebUser.id == WebUserResetPasswordToken.web_user_id)
                           .join(Survey, Survey.id == WebUser.survey_id)
                           .order_by(WebUserResetPasswordToken.active.desc(),
                                     WebUserResetPasswordToken.modified_at.desc())
                           .filter(WebUserResetPasswordToken.created_at == subquery.c.latest))
        if email:
            email_filter = email + '%'
            query = query.filter(WebUser.email.ilike(email_filter))
        return query

    def disable(self, token_id):
        token = WebUserResetPasswordToken.query.get(token_id)
        token.active = False
        db.session.commit()
        return token
