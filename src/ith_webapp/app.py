from decimal import Decimal

from flask import Flask, current_app, redirect, render_template_string, url_for

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


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)

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
        return redirect(url_for("customers.customer_list"))

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

    from ith_webapp.views.field_service import bp as field_services_bp
    app.register_blueprint(field_services_bp)

    from ith_webapp.views.projects import bp as projects_bp
    app.register_blueprint(projects_bp)

    from ith_webapp.views.order_confirmations import bp as order_confirmations_bp
    app.register_blueprint(order_confirmations_bp)

    from ith_webapp.views.audit_trail import bp as audit_trail_bp
    app.register_blueprint(audit_trail_bp)

    from ith_webapp.views.ith_test_gauges import bp as ith_test_gauges_bp
    app.register_blueprint(ith_test_gauges_bp)

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
