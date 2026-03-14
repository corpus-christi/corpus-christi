import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import create_app
from .db import Base, get_db
from .auth.dependencies import create_access_token


TEST_DATABASE_URL = "sqlite:///:memory:"


def make_test_engine():
    return create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )


def client_factory(authenticated: bool = True):
    engine = make_test_engine()
    TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app()

    def override_get_db():
        with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app, raise_server_exceptions=True)

    if authenticated:
        token = create_access_token(data={"sub": "test-user", "roles": []})
        client.headers.update({"Authorization": f"Bearer {token}"})

    return client, engine, TestingSessionLocal


@pytest.fixture
def auth_client():
    client, engine, session_factory = client_factory(authenticated=True)
    yield client, session_factory()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def plain_client():
    client, engine, session_factory = client_factory(authenticated=False)
    yield client, session_factory()
    Base.metadata.drop_all(bind=engine)
