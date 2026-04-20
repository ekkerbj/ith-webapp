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


def test_login_page_uses_shared_layout_and_styles(client):
    response = client.get("/login?next=/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'href="/static/style.css"' in body
    assert "<main>" in body
    assert "Login" in body


def test_missing_route_renders_custom_404_page():
    app = create_app(testing=True)
    client = app.test_client()

    response = client.get("/missing-page")
    body = response.get_data(as_text=True)

    assert response.status_code == 404
    assert "Page not found" in body
    assert "Return to switchboard" in body


def test_unhandled_exception_renders_custom_500_page_and_logs_context(caplog):
    app = create_app(testing=True)

    @app.route("/boom")
    def boom():
        raise RuntimeError("boom")

    client = app.test_client()

    with caplog.at_level("ERROR"):
        response = client.get("/boom")

    body = response.get_data(as_text=True)

    assert response.status_code == 500
    assert "Internal server error" in body

    records = [record for record in caplog.records if record.getMessage() == "Unhandled application exception"]
    assert len(records) == 1
    assert records[0].request_method == "GET"
    assert records[0].request_path == "/boom"
    assert records[0].exception_type == "RuntimeError"


def test_stylesheet_is_served_with_responsive_rules(client):
    response = client.get("/static/style.css")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "@media" in body
    assert "max-width" in body


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


def test_create_app_uses_database_url_environment_variable(monkeypatch):
    captured = {}

    def fake_create_session_factory(database_url="sqlite:///:memory:"):
        captured["database_url"] = database_url

        class FakeSession:
            def get_bind(self):
                return object()

        return lambda: FakeSession()

    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:pass@db.example.com/ith",
    )
    monkeypatch.setattr("ith_webapp.app.create_session_factory", fake_create_session_factory)
    monkeypatch.setattr("ith_webapp.app.Base.metadata.create_all", lambda bind: None)

    create_app()

    assert captured["database_url"] == "postgresql+psycopg://user:pass@db.example.com/ith"
