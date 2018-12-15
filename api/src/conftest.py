import pytest

from . import sqla as _sqla, create_app


@pytest.fixture()
def app():
    """Create an app instance configured for testing."""
    return create_app('test')


@pytest.fixture
def client(app):
    """Create a Flask test client."""
    return app.test_client()


@pytest.fixture()
def sqla(app):
    _sqla.app = app
    _sqla.drop_all()
    _sqla.create_all()
    return _sqla


@pytest.fixture()
def session(sqla):
    session = sqla.create_scoped_session()
    sqla.session = session
    yield session
    session.remove()
