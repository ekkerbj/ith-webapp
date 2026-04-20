import pytest
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base


@pytest.fixture
def engine():
    eng = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()


@pytest.fixture
def session(engine) -> Session:
    factory = sessionmaker(bind=engine)
    s = factory()
    yield s
    s.close()


@pytest.fixture
def app():
    return create_app(testing=True)


@pytest.fixture
def client(app) -> FlaskClient:
    app.config["FIREBASE_AUTH_CLIENT"] = lambda email, password: {
        "email": email,
        "idToken": "test-id-token",
        "refreshToken": "test-refresh-token",
        "localId": "test-local-id",
    }
    client = app.test_client()
    client.post(
        "/login?next=/",
        data={"email": "tester@example.com", "password": "password"},
    )
    return client


@pytest.fixture
def guest_client(app) -> FlaskClient:
    app.config["AUTH_REQUIRED"] = True
    return app.test_client()
