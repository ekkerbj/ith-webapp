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
    return app.test_client()
