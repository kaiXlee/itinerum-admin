#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Kyle Fitzsimmons, 2017
import pytest

from admin.server import create_app
from models import db as _db


## Testing setup & teardown fixtures ==========================================
# create the testing flask application
@pytest.fixture(scope='session')
def app(request):
    app = create_app(testing=True)

    # initialize an application context before running tests
    ctx = app.app_context()
    ctx.push()
    yield app
    ctx.pop()


# setup and remove the testing database
@pytest.fixture(scope='function')
def db(app, request):
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()


@pytest.fixture(autouse=True)
def session(db, monkeypatch, request):
    connection = db.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection)
    session = db.create_scoped_session(options=options)
    monkeypatch.setattr(db, 'session', session)
    yield session
    transaction.rollback()
    connection.close()
    session.remove()


@pytest.fixture
def client(app, db):
    with app.test_client() as client:
        yield client
