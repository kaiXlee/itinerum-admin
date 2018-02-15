#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017
from admin.db import activity, survey_admin, token, user_lookup


class Database:
    def __init__(self):
        self.activity = activity.RecentActivityActions()
        self.survey_admin = survey_admin.SurveyAdminActions()
        self.token = token.TokenActions()
        self.user_lookup = user_lookup.UserLookupActions()
