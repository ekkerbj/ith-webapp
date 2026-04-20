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
    login_page = client.get("/login?next=/")
    body = login_page.get_data(as_text=True)
    csrf_token = None
    if 'name="csrf_token" value="' in body:
        csrf_token = body.split('name="csrf_token" value="', 1)[1].split('"', 1)[0]
    form_data = {"email": "tester@example.com", "password": "password"}
    if csrf_token is not None:
        form_data["csrf_token"] = csrf_token
    client.post("/login?next=/", data=form_data)
    return client


@pytest.fixture
def guest_client(app) -> FlaskClient:
    app.config["AUTH_REQUIRED"] = True
    return app.test_client()
