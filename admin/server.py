#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017-2018
from flask import Flask, jsonify, make_response
from flask_migrate import Migrate
from flask_security import Security
import logging
from raven.contrib.flask import Sentry
import os

from admin.blueprints import (account_recovery, control_panel, manage_surveys, 
                              recent_activity, researcher_tokens, signup_tokens,
                              user_lookup)
import config
from models import db, user_datastore


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_app_config(testing):
    if testing is True:
        logger.info(' * Loading TESTING server configuration...')
        return config.AdminTestingConfig

    # fallback on env variable
    elif os.environ.get('CONFIG') == 'debug':
        logger.info(' * Loading DEVELOPMENT server configuration...')
        return config.AdminDevelopmentConfig
    elif os.environ.get('CONFIG') == 'testing':
        logger.info(' * Loading TESTING server configuration...')
        return config.AdminTestingConfig
    else:
        logger.info(' * Loading PRODUCTION server configuration...')
        return config.AdminProductionConfig


def create_app(testing=False):
    app = Flask(__name__)
    cfg = load_app_config(testing)
    app.config.from_object(cfg)
    Security(app, user_datastore)
    db.init_app(app)

    # Connect Alembic with Flask-Migrate =======================================
    Migrate(app, db)

    # Connect Sentry.io error reporting ========================================
    if app.config['CONF'] == 'production':
        logger.info(' * Starting Sentry.io reporting for application...')
        Sentry(app, dsn='https://{key}:{secret}@sentry.io/{app_id}'.format(
            key=app.config['SENTRY_KEY'],
            secret=app.config['SENTRY_SECRET'],
            app_id=app.config['SENTRY_APP_ID']))
    else:
        logger.info(' * Sentry.io reporting disabled.')

    # Register admin dashboard blueprint =======================================
    app.register_blueprint(control_panel.blueprint)
    app.register_blueprint(account_recovery.blueprint, url_prefix='/account-recovery')
    app.register_blueprint(manage_surveys.blueprint, url_prefix='/manage-surveys')
    app.register_blueprint(recent_activity.blueprint, url_prefix='/recent-activity')
    app.register_blueprint(researcher_tokens.blueprint, url_prefix='/researcher-tokens')
    app.register_blueprint(signup_tokens.blueprint, url_prefix='/signup-tokens')
    app.register_blueprint(user_lookup.blueprint, url_prefix='/user-lookup')

    # Register health check route for load balancer ============================
    @app.route('/health')
    def ecs_health_check():
        response = {'status': 0}
        return make_response(jsonify(response))  
    return app
