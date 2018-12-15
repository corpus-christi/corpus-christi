import pytest

from src import db as _db, create_app


@pytest.fixture()
def app():
    return create_app('test')


@pytest.fixture
def client(app):
    return app.test_client()


# @pytest.fixture()
# def db(app, request):
#     _db.app = app
#     _db.create_all()
#     yield _db
#     _db.drop_all()
#
#
# @pytest.fixture(scope='session')
# def session(db, request):
#     session = db.create_scoped_session()
#     db.session = session
#     yield session
#     session.remove()
