#!/usr/bin/env python
# Kyle Fitzsimmons 2016-2018
# WSGI entry script for allowing API to be managed by gunicorn
from admin.server import create_app

app = create_app()


if __name__ == "__main__":
    if app.config.get('CONF') in ['development', 'testing']:
        app.run(host=app.config['APP_HOST'],
                port=app.config['APP_PORT'],
                debug=True)
    else:
        app.run(host='0.0.0.0',
                port=app.config['APP_PORT'])
