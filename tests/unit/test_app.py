from flask import Flask

from ith_webapp.database import Base, init_db
from ith_webapp.app import create_app


def test_create_app_returns_flask_instance():
    app = create_app(testing=True)

    assert isinstance(app, Flask)


def test_index_renders_switchboard(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Switchboard" in body
    assert "Customers" in body
    assert "Check In" in body
    assert "Services" in body
    assert "Packing Lists" in body
    assert "Parts" in body
    assert "Field Service" in body
    assert "Reports" in body
    assert "Admin" in body


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
