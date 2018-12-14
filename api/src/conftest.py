import pytest

from src import create_app, db as _db


@pytest.fixture(scope='session')
def app():
    app = create_app('test')
    return app


@pytest.fixture(scope='session')
def db(app, request):
    _db.app = app
    _db.create_all()
    yield _db
    _db.drop_all()


@pytest.fixture(scope='session')
def session(db, request):
    session = db.create_scoped_session()
    db.session = session
    yield session
    session.remove()
