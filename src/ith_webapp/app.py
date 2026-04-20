from decimal import Decimal
import json
import os
from urllib import error, request as urllib_request

from flask import Flask, abort, current_app, redirect, render_template_string, request, session, url_for
from sqlalchemy import func
from werkzeug.exceptions import HTTPException

from ith_webapp.database import Base, create_session_factory
from ith_webapp.models.audit_trail import AuditTrail
from ith_webapp.models.check_in import CheckInSub
from ith_webapp.models.packing_list import PackingList
from ith_webapp.models.service import Service
from ith_webapp.views.session import register_session_middleware


def _calculate_reorder_quantity(stock) -> Decimal:
    return stock.min_stock - stock.on_hand + stock.committed - stock.on_order


def _inventory_reorder_rows():
    repository = current_app.config["INVENTORY_REORDER_REPOSITORY"]
    warehouse_code = current_app.config["INVENTORY_REORDER_WAREHOUSE_CODE"]
    item_codes = current_app.config.get("INVENTORY_REORDER_ITEM_CODES", [])

    rows = []
    for item_code in item_codes:
        stock = repository.get_stock(item_code, warehouse_code)
        if stock is None:
            continue
        reorder_quantity = _calculate_reorder_quantity(stock)
        if reorder_quantity > 0:
            rows.append(
                {
                    "item_code": stock.item_code,
                    "reorder_quantity": reorder_quantity,
                }
            )
    return rows


def _dashboard_counts(session) -> dict[str, int]:
    open_check_ins = (
        session.query(func.count(CheckInSub.id))
        .filter(CheckInSub.closed.is_(False))
        .scalar()
    )
    pending_quotes = (
        session.query(func.count(Service.service_id))
        .filter(
            Service.active.is_(True),
            Service.completed_date.is_(None),
            Service.quoted_date.is_(None),
        )
        .scalar()
    )
    ready_to_ship = session.query(func.count(PackingList.id)).scalar()
    open_services = (
        session.query(func.count(Service.service_id))
        .filter(Service.active.is_(True), Service.completed_date.is_(None))
        .scalar()
    )
    return {
        "open_check_ins": open_check_ins or 0,
        "pending_quotes": pending_quotes or 0,
        "ready_to_ship": ready_to_ship or 0,
        "open_services": open_services or 0,
    }


def _recent_activity(session, limit: int = 5) -> list[AuditTrail]:
    return (
        session.query(AuditTrail)
        .order_by(AuditTrail.changed_at.desc(), AuditTrail.audit_trail_id.desc())
        .limit(limit)
        .all()
    )


ERROR_PAGE_TEMPLATE = """
{% extends "base.html" %}
{% block title %}{{ code }} - ITH{% endblock %}
{% block content %}
<section class="error-page error-page--{{ code }}">
  <h1>{{ heading }}</h1>
  <p>{{ message }}</p>
  <p><a href="{{ url_for('index') }}">Return to switchboard</a></p>
</section>
{% endblock %}
"""


def _render_error_page(code: int, heading: str, message: str):
    return render_template_string(
        ERROR_PAGE_TEMPLATE,
        code=code,
        heading=heading,
        message=message,
    )


def _log_unhandled_exception(exc: Exception) -> None:
    current_app.logger.exception(
        "Unhandled application exception",
        extra={
            "request_method": request.method,
            "request_path": request.path,
            "exception_type": exc.__class__.__name__,
        },
    )


def _firebase_sign_in(api_key: str, email: str, password: str) -> dict[str, str]:
    payload = json.dumps(
        {"email": email, "password": password, "returnSecureToken": True}
    ).encode("utf-8")
    auth_url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={api_key}"
    )
    req = urllib_request.Request(
        auth_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib_request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8")
        raise ValueError(detail or "Firebase authentication failed") from exc


SALES_BLUEPRINTS = {
    "customers",
    "consignment_list",
    "demo_contracts",
    "order_confirmations",
    "parts",
    "projects",
}
TECHNICIAN_BLUEPRINTS = {
    "field_services",
    "ith_test_gauges",
    "rentals",
    "sites_gas_turbines",
    "sites_wind_gas",
    "sites_wind_turbines",
    "wind_turbine_leads",
    "wind_turbine_leads_details",
}


def _resolve_role(payload: dict[str, object], default_role: str = "admin") -> str:
    custom_claims = payload.get("customClaims")
    if isinstance(custom_claims, dict):
        role = custom_claims.get("role")
        if isinstance(role, str) and role:
            return role
    role = payload.get("role")
    if isinstance(role, str) and role:
        return role
    return default_role


def _current_role() -> str:
    user = session.get("firebase_user") or {}
    role = user.get("role") if isinstance(user, dict) else None
    return role if isinstance(role, str) and role else "admin"


def _is_mutating_view() -> bool:
    return request.method != "GET" or request.path.endswith(("/new", "/edit", "/delete"))


def _endpoint_blueprint(endpoint: str | None) -> str | None:
    if endpoint is None:
        return None
    return endpoint.split(".", 1)[0]


def _authorize_request() -> None:
    endpoint = request.endpoint
    if endpoint in {"static", "login", "login_post", "logout"}:
        return

    role = _current_role()
    if role == "admin":
        return

    if endpoint is not None and endpoint.startswith("audit_trail."):
        abort(403)

    if not _is_mutating_view():
        return

    blueprint = _endpoint_blueprint(endpoint)
    if blueprint in SALES_BLUEPRINTS:
        if role != "sales":
            abort(403)
        return

    if blueprint in TECHNICIAN_BLUEPRINTS:
        if role != "technician":
            abort(403)
        return

    if role == "readonly":
        abort(403)


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.secret_key = app.config.get("SECRET_KEY") or "dev-only-secret-key"
    app.config["AUTH_REQUIRED"] = not testing
    app.config.setdefault("LIST_PAGE_SIZE", 20)

    if testing:
        app.config["TESTING"] = True
        app.config["DATABASE_URL"] = "sqlite:///:memory:"
    else:
        app.config.setdefault("DATABASE_URL", os.getenv("DATABASE_URL", "sqlite:///ith.db"))

    if "SESSION_FACTORY" not in app.config:
        import ith_webapp.models  # noqa: F401 — register models with Base

        database_url = app.config["DATABASE_URL"]
        factory = create_session_factory(database_url)
        Base.metadata.create_all(factory().get_bind())
        app.config["SESSION_FACTORY"] = factory

    register_session_middleware(app)

    @app.route("/")
    def index():
        session = app.config["SESSION_FACTORY"]()
        try:
            summary = _dashboard_counts(session)
            activity = _recent_activity(session)
        finally:
            session.close()
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Dashboard - ITH{% endblock %}
            {% block content %}
            <h1>Dashboard</h1>
            <section>
              <h2>Summary</h2>
              <dl>
                <div><dt>Open Check-Ins</dt><dd>{{ summary.open_check_ins }}</dd></div>
                <div><dt>Pending Quotes</dt><dd>{{ summary.pending_quotes }}</dd></div>
                <div><dt>Ready to Ship</dt><dd>{{ summary.ready_to_ship }}</dd></div>
                <div><dt>Open Services</dt><dd>{{ summary.open_services }}</dd></div>
              </dl>
            </section>
            <section>
              <h2>Recent Activity</h2>
              <table>
                <thead>
                  <tr>
                    <th>When</th>
                    <th>Table</th>
                    <th>Field</th>
                    <th>Action</th>
                    <th>User</th>
                  </tr>
                </thead>
                <tbody>
                  {% if activity %}
                  {% for row in activity %}
                  <tr>
                    <td>{{ row.changed_at.isoformat() }}</td>
                    <td>{{ row.table_name }}</td>
                    <td>{{ row.field_name }}</td>
                    <td>{{ row.action }}</td>
                    <td>{{ row.changed_by or "" }}</td>
                  </tr>
                  {% endfor %}
                  {% else %}
                  <tr><td colspan="5">(none)</td></tr>
                  {% endif %}
                </tbody>
              </table>
            </section>
            <section>
              <h2>Quick Access</h2>
              <ul>
                <li><a href="{{ url_for('customers.customer_list') }}">Customer List</a></li>
                <li><a href="{{ url_for('reports.open_repair_list_report') }}">Open Repair List</a></li>
                <li><a href="{{ url_for('packing_list_workflow.packing_list_index') }}">Packing List Index</a></li>
                <li><a href="{{ url_for('packing_list_workflow.ready_to_ship') }}">Ready to Ship</a></li>
                <li><a href="{{ url_for('field_services.field_service_list') }}">Field Services</a></li>
                <li><a href="{{ url_for('inventory_reorder_dashboard') }}">Inventory Reorder Dashboard</a></li>
                <li><a href="{{ url_for('reports.audit_trail_report') }}">Audit Trail</a></li>
              </ul>
            </section>
            {% endblock %}
            """,
            summary=summary,
            activity=activity,
        )

    @app.before_request
    def require_authentication():
        if not app.config.get("AUTH_REQUIRED", True):
            return None
        if request.endpoint in {"static", "login", "login_post", "logout"}:
            return None
        if session.get("firebase_user") is None:
            next_url = request.full_path.rstrip("?")
            return redirect(url_for("login", next=next_url))
        _authorize_request()

    @app.route("/login", methods=["GET"])
    def login():
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Login - ITH{% endblock %}
            {% block content %}
            <h1>Login</h1>
            <form method="post">
              <label>Email <input type="email" name="email"></label>
              <label>Password <input type="password" name="password"></label>
              <button type="submit">Sign in</button>
            </form>
            {% endblock %}
            """
        )

    @app.route("/login", methods=["POST"])
    def login_post():
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        auth_client = app.config.get("FIREBASE_AUTH_CLIENT")
        if auth_client is None:
            api_key = app.config.get("FIREBASE_API_KEY")
            if not api_key:
                raise RuntimeError("FIREBASE_API_KEY is required for login")
            auth_client = lambda auth_email, auth_password: _firebase_sign_in(
                api_key, auth_email, auth_password
            )
        payload = auth_client(email, password)
        session["firebase_user"] = {
            "email": payload["email"],
            "id_token": payload.get("idToken"),
            "refresh_token": payload.get("refreshToken"),
            "local_id": payload.get("localId"),
            "role": _resolve_role(payload),
        }
        session.permanent = True
        next_url = request.args.get("next") or url_for("customers.customer_list")
        return redirect(next_url)

    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/inventory/reorder")
    def inventory_reorder_dashboard():
        rows = _inventory_reorder_rows()
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Inventory Reorder Dashboard - ITH{% endblock %}
            {% block content %}
            <h1>Inventory Reorder Dashboard</h1>
            <section>
              <table>
                <thead>
                  <tr><th>Item</th><th>Reorder Quantity</th></tr>
                </thead>
                <tbody>
                  {% for row in rows %}
                    <tr><td>{{ row.item_code }}</td><td>{{ row.reorder_quantity }}</td></tr>
                  {% endfor %}
                </tbody>
              </table>
            </section>
            {% endblock %}
            """,
            rows=rows,
        )

    @app.errorhandler(404)
    def not_found(_error):
        return (
            _render_error_page(
                404,
                "Page not found",
                "The page you requested could not be found.",
            ),
            404,
        )

    @app.errorhandler(Exception)
    def internal_server_error(exc):
        if isinstance(exc, HTTPException):
            return exc
        _log_unhandled_exception(exc)
        return (
            _render_error_page(
                500,
                "Internal server error",
                "Something went wrong while processing your request.",
            ),
            500,
        )

    from ith_webapp.views.customers import bp as customers_bp

    app.register_blueprint(customers_bp)

    from ith_webapp.views.parts import bp as parts_bp
    app.register_blueprint(parts_bp)

    from ith_webapp.views.consignment_list import bp as consignment_list_bp
    app.register_blueprint(consignment_list_bp)

    from ith_webapp.views.rentals import bp as rentals_bp
    app.register_blueprint(rentals_bp)

    from ith_webapp.views.demo_contracts import bp as demo_contracts_bp
    app.register_blueprint(demo_contracts_bp)

    from ith_webapp.views.field_service import bp as field_services_bp
    app.register_blueprint(field_services_bp)

    from ith_webapp.views.projects import bp as projects_bp
    app.register_blueprint(projects_bp)

    from ith_webapp.views.order_confirmations import bp as order_confirmations_bp
    app.register_blueprint(order_confirmations_bp)

    from ith_webapp.views.warranty_claims import bp as warranty_claims_bp
    app.register_blueprint(warranty_claims_bp)

    from ith_webapp.views.audit_trail import bp as audit_trail_bp
    app.register_blueprint(audit_trail_bp)

    from ith_webapp.views.ith_test_gauges import bp as ith_test_gauges_bp
    app.register_blueprint(ith_test_gauges_bp)

    from ith_webapp.reports import bp as reports_bp
    app.register_blueprint(reports_bp)

    # Register Packing List Workflow blueprint
    from ith_webapp.views.packing_list_workflow import bp as packing_list_workflow_bp
    app.register_blueprint(packing_list_workflow_bp)

    from ith_webapp.views.wind_turbine_tracking import (
        site_gas_turbines_bp,
        site_wind_gas_bp,
        site_wind_turbines_bp,
        wind_turbine_lead_details_bp,
        wind_turbine_leads_bp,
    )
    app.register_blueprint(site_gas_turbines_bp)
    app.register_blueprint(site_wind_turbines_bp)
    app.register_blueprint(site_wind_gas_bp)
    app.register_blueprint(wind_turbine_leads_bp)
    app.register_blueprint(wind_turbine_lead_details_bp)

    return app
