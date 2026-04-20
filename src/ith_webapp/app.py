from decimal import Decimal
import json
from urllib import error, request as urllib_request

from flask import Flask, abort, current_app, redirect, render_template_string, request, session, url_for

from ith_webapp.database import Base, create_session_factory


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

    if "SESSION_FACTORY" not in app.config:
        import ith_webapp.models  # noqa: F401 — register models with Base

        database_url = app.config.get("DATABASE_URL", "sqlite:///ith.db")
        factory = create_session_factory(database_url)
        Base.metadata.create_all(factory().get_bind())
        app.config["SESSION_FACTORY"] = factory

    @app.route("/")
    def index():
        sections = [
            ("Customers", [("Customer List", "customers.customer_list")]),
            ("Check In", [("Check In workflow coming soon", None)]),
            (
                "Services",
                [
                    ("Projects", "projects.project_list"),
                    ("Demo Contracts", "demo_contracts.demo_contract_list"),
                    ("Order Confirmations", "order_confirmations.order_confirmation_list"),
                    ("Warranty Claims", "warranty_claims.warranty_claim_list"),
                ],
            ),
            (
                "Packing Lists",
                [
                    ("Consignment Lists", "consignment_list.consignment_list"),
                    ("Packing List Index", "packing_list_workflow.packing_list_index"),
                    ("Ready to Produce", "packing_list_workflow.ready_to_produce"),
                    ("Ready to Ship", "packing_list_workflow.ready_to_ship"),
                ],
            ),
            ("Parts", [("Parts", "parts.part_list")]),
            (
                "Field Service",
                [
                    ("Field Services", "field_services.field_service_list"),
                    ("Gas Turbines", "sites_gas_turbines.list"),
                    ("Wind Turbines", "sites_wind_turbines.list"),
                    ("Wind Gas Sites", "sites_wind_gas.list"),
                    ("Wind Leads", "wind_turbine_leads.list"),
                    ("Lead Details", "wind_turbine_leads_details.list"),
                ],
            ),
            (
                "Reports",
                [("Inventory Reorder Dashboard", "inventory_reorder_dashboard"), ("Audit Trail", None)],
            ),
            ("Admin", [("Login/logout and access controls", None)]),
        ]
        return render_template_string(
            """
            {% extends "base.html" %}
            {% block title %}Switchboard - ITH{% endblock %}
            {% block content %}
            <h1>Switchboard</h1>
            {% for heading, links in sections %}
            <section>
              <h2>{{ heading }}</h2>
              <ul>
                {% for label, endpoint in links %}
                <li>
                  {% if endpoint %}
                  <a href="{{ url_for(endpoint) }}">{{ label }}</a>
                  {% else %}
                  {{ label }}
                  {% endif %}
                </li>
                {% endfor %}
              </ul>
            </section>
            {% endfor %}
            {% endblock %}
            """,
            sections=sections,
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
            <!doctype html>
            <html lang="en">
            <head><title>Inventory Reorder Dashboard</title></head>
            <body>
              <h1>Inventory Reorder Dashboard</h1>
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
            </body>
            </html>
            """,
            rows=rows,
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
