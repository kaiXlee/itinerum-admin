#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2018
from flask import current_app, request
from functools import wraps


def check_auth(username, password):
    return username == current_app.config['ADMIN_USER'] and \
           password == current_app.config['ADMIN_PASSWORD']


# HTTP Basic Auth decorator
def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            message = ('Could not verify your access level for that URL.\n'
                       'You have to login with proper credentials.')
            headers = {'WWW-Authenticate': 'Basic realm="Login Required"'}
            return Response(message, 401, headers)
        return f(*args, **kwargs)
    return decorated
