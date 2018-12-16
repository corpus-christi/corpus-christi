import pytest

from . import orm as _orm, create_app


@pytest.fixture()
def app():
    """Create an app instance configured for testing."""
    app = create_app('test')
    app.testing = True      # Make sure exceptions percolate out
    return app


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    with app.test_request_context():
        with app.test_client() as client:
            yield client


@pytest.fixture()
def orm(app):
    """Inject the ORM (SQLAlchemy)"""
    _orm.app = app
    _orm.drop_all()
    _orm.create_all()
    return _orm


@pytest.fixture()
def dbs(orm):
    """Inject a database session."""
    session = orm.create_scoped_session()
    orm.session = session
    yield session
    session.remove()
