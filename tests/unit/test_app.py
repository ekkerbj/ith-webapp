from flask import Flask

from ith_webapp.database import Base, init_db
from ith_webapp.app import create_app


def test_create_app_returns_flask_instance():
    app = create_app(testing=True)

    assert isinstance(app, Flask)


def test_index_redirects_to_customers(client):
    response = client.get("/")

    assert response.status_code == 302
    assert "/customers" in response.headers["Location"]


def test_default_startup_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app()
    app.config["DATABASE_URL"] = f"sqlite:///{db_path}"
    # Force re-initialization with the file-based DB
    from sqlalchemy import inspect
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    inspector = inspect(session.get_bind())
    table_names = inspector.get_table_names()
    session.close()

    assert "customer" in table_names
