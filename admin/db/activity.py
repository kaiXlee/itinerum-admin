#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017
from datetime import datetime, timedelta
from models import db, MobileCoordinate, PromptResponse
import pytz


class RecentActivityActions:

    def coordinates_by_times(self, start, end):
        query = (MobileCoordinate.query.filter(db.and_(MobileCoordinate.timestamp >= start,
                                                       MobileCoordinate.timestamp <= end))
                                       .order_by(MobileCoordinate.mobile_id, MobileCoordinate.timestamp.desc())
                                       .distinct(MobileCoordinate.mobile_id))
        return query

    def prompts_by_times(self, start, end):
        query = (PromptResponse.query.filter(db.and_(PromptResponse.timestamp >= start,
                                                     PromptResponse.timestamp <= end))
                                     .order_by(PromptResponse.mobile_id, PromptResponse.timestamp.desc()))
        return query

    def coordinates_by_mobile_id(self, mobile_id):
        min_time = datetime(2016, 1, 1, 0, 0, 0, tzinfo=pytz.utc)
        query = (MobileCoordinate.query.filter_by(mobile_id=mobile_id)
                                       .filter(MobileCoordinate.timestamp >= min_time)
                                       .order_by(MobileCoordinate.timestamp.asc())
                                       .limit(5000))
        return query
