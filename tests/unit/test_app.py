from flask import Flask

from ith_webapp.database import Base, init_db
from ith_webapp.app import create_app
from ith_webapp.models.check_in import CheckIn, CheckInSub
from ith_webapp.models.customer import Customer
from ith_webapp.models.packing_list import PackingList
from ith_webapp.models.service import Service
from ith_webapp.services.audit_trail import record_audit_change


def test_create_app_returns_flask_instance():
    app = create_app(testing=True)

    assert isinstance(app, Flask)


def test_create_app_uses_secure_cookie_settings_in_production(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "prod-secret-key")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")

    app = create_app()

    assert app.secret_key == "prod-secret-key"
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.permanent_session_lifetime.days == 7


def test_index_renders_switchboard(client):
    response = client.get("/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Dashboard" in body
    assert "Open Check-Ins" in body
    assert "Pending Quotes" in body
    assert "Ready to Ship" in body
    assert "Open Services" in body


def test_index_dashboard_shows_summary_counts_recent_activity_and_quick_links(app):
    session = app.config["SESSION_FACTORY"]()
    try:
        customer = Customer(customer_name="Acme")
        session.add(customer)
        session.flush()

        check_in = CheckIn(customer_id=customer.customer_id)
        session.add(check_in)
        session.flush()

        session.add(CheckInSub(check_in_id=check_in.id, tool_id=1001, closed=False))
        session.add(
            Service(
                customer_id=customer.customer_id,
                active=True,
                order_status="Open",
                quote_status=None,
                quoted_date=None,
                completed_date=None,
            )
        )
        session.add(PackingList(customer_name="Acme", packing_date="2026-04-20"))
        record_audit_change(
            session,
            table_name="customer",
            record_id=customer.customer_id,
            action="update",
            changes={"customer_name": ("Old Name", "Acme")},
            changed_by="tester@example.com",
        )
        session.commit()

        response = app.test_client().get("/")
        body = response.get_data(as_text=True)

        assert response.status_code == 200
        assert "1" in body
        assert "Recent Activity" in body
        assert "customer_name" in body
        assert "tester@example.com" in body
        assert "Quick Access" in body
        assert "Customer List" in body
        assert "Packing List Index" in body
    finally:
        session.close()


def test_login_page_uses_shared_layout_and_styles(client):
    response = client.get("/login?next=/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'href="/static/style.css"' in body
    assert 'class="app-shell__content"' in body
    assert "Login" in body
    assert 'name="csrf_token"' in body


def test_login_page_exposes_pwa_metadata_and_app_shell_markup(client):
    response = client.get("/login?next=/")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'rel="manifest"' in body
    assert 'name="theme-color"' in body
    assert 'class="app-shell__header"' in body
    assert 'class="app-shell__nav"' in body


def test_login_post_stores_only_minimal_firebase_session(client, app):
    app.config["FIREBASE_AUTH_CLIENT"] = lambda email, password: {
        "email": email,
        "idToken": "token-123",
        "refreshToken": "refresh-123",
        "localId": "local-123",
        "role": "sales",
    }

    login_page = client.get("/login?next=/customers/")
    csrf_token = login_page.get_data(as_text=True).split('name="csrf_token" value="')[1].split('"', 1)[0]

    response = client.post(
        "/login?next=/customers/",
        data={"email": "user@example.com", "password": "secret", "csrf_token": csrf_token},
    )

    assert response.status_code == 302
    with client.session_transaction() as session:
        firebase_user = session.get("firebase_user")
        assert firebase_user == {
            "email": "user@example.com",
            "local_id": "local-123",
            "role": "sales",
        }


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


def test_stylesheet_includes_list_row_formatting_rules(client):
    response = client.get("/static/style.css")
    body = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "tbody tr:nth-child(even)" in body
    assert "tbody tr:hover" in body
    assert "tbody tr:focus-within" in body


def test_default_startup_creates_tables(tmp_path):
    db_path = tmp_path / "test.db"
    from os import environ
    environ["SECRET_KEY"] = "prod-secret-key"
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
    monkeypatch.setenv("SECRET_KEY", "prod-secret-key")
    monkeypatch.delenv("SESSION_COOKIE_SECURE", raising=False)
    monkeypatch.setattr("ith_webapp.app.create_session_factory", fake_create_session_factory)
    monkeypatch.setattr("ith_webapp.app.Base.metadata.create_all", lambda bind: None)

    create_app()

    assert captured["database_url"] == "postgresql+psycopg://user:pass@db.example.com/ith"
