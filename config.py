#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
#
# Configuration file to pass to api/__init__.py for creating Flask app
# with different run levels
from datetime import timedelta
import os


DEFAULT_DEV_DB = 'postgresql://127.0.0.1/itinerum_dev'
DEFAULT_TEST_DB = 'postgresql://127.0.0.1/itinerum_test'
DEFAULT_PRODUCTION_DB = 'postgresql://127.0.0.1/itinerum'


class Config(object):
    CONF = 'base'
    APP_HOST = '0.0.0.0'
    APP_PORT = int(os.environ.get('IT_ADMIN_PORT', 9002))
    SECRET_KEY = os.environ.get('IT_SECRET_KEY', 'ChangeMe')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Admin API config ===========================================================
class AdminConfig(Config):
    APP_NAME = 'ItinerumAdmin'
    ADMIN_USER = os.environ.get('IT_ADMIN_USER', 'admin')
    ADMIN_PASSWORD = os.environ.get('IT_ADMIN_PASSWORD', 'admin')


class AdminDevelopmentConfig(AdminConfig):
    CONF = 'development'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('IT_POSTGRES_URI', DEFAULT_DEV_DB)


class AdminTestingConfig(AdminConfig):
    CONF = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('IT_POSTGRES_URI', DEFAULT_TEST_DB)


class AdminProductionConfig(AdminConfig):
    CONF = 'production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('IT_POSTGRES_URI', DEFAULT_PRODUCTION_DB)
    SENTRY_KEY = os.environ.get('SENTRY_KEY')
    SENTRY_SECRET = os.environ.get('SENTRY_SECRET')
    SENTRY_APP_ID = os.environ.get('SENTRY_APP_ID')
