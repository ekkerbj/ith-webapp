from ith_webapp.models import (
    Customer,
    CustomerApplication,
    CustomerApplicationSpecs,
    CustomerMarket,
    CustomerTools,
    Market,
    Unit,
)


def test_customer_detail_report_includes_customer_profile_data(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(
            customer_name="Acme",
            card_code="C-100",
            active=True,
            website="https://acme.example",
            comments="Primary account",
        )
        market = Market(name="North America")
        session.add_all([customer, market])
        session.flush()
        session.add(CustomerMarket(customer_id=customer.customer_id, market_id=market.market_id))
        application = CustomerApplication(
            customer_id=customer.customer_id,
            name="Calibration",
            description="Used for torque checks",
        )
        session.add(application)
        session.flush()
        session.add(
            CustomerApplicationSpecs(
                application_id=application.id,
                key="Voltage",
                value="120V",
            )
        )
        session.commit()

        response = app.test_client().get(f"/reports/customers/{customer.customer_id}")

        assert response.status_code == 200
        assert response.mimetype == "text/html"
        assert b"Customer Report" in response.data
        assert b"Acme" in response.data
        assert b"C-100" in response.data
        assert b"North America" in response.data
        assert b"Calibration" in response.data
        assert b"Voltage" in response.data
        assert b"120V" in response.data
    finally:
        session.close()


def test_customer_reports_by_region_and_responsibility_group_customers(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        north = Market(name="North")
        south = Market(name="South")
        acme = Customer(customer_name="Acme", responsibility_id=12)
        beta = Customer(customer_name="Beta", responsibility_id=12)
        gamma = Customer(customer_name="Gamma", responsibility_id=45)
        session.add_all([north, south, acme, beta, gamma])
        session.flush()
        session.add_all(
            [
                CustomerMarket(customer_id=acme.customer_id, market_id=north.market_id),
                CustomerMarket(customer_id=beta.customer_id, market_id=north.market_id),
                CustomerMarket(customer_id=gamma.customer_id, market_id=south.market_id),
            ]
        )
        session.commit()

        region_response = app.test_client().get("/reports/customers/by-region")
        responsibility_response = app.test_client().get(
            "/reports/customers/by-responsibility"
        )

        assert region_response.status_code == 200
        assert b"North" in region_response.data
        assert b"South" in region_response.data
        assert b"Acme" in region_response.data
        assert b"Beta" in region_response.data
        assert b"Gamma" in region_response.data

        assert responsibility_response.status_code == 200
        assert b"Responsibility 12" in responsibility_response.data
        assert b"Responsibility 45" in responsibility_response.data
        assert b"Acme" in responsibility_response.data
        assert b"Gamma" in responsibility_response.data
    finally:
        session.close()


def test_customer_reports_pricing_and_tools_inventory(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(
            customer_name="Acme",
            card_code="C-100",
            multiplier=1.25,
        )
        unit = Unit(name="Press")
        session.add_all([customer, unit])
        session.flush()
        session.add(
            CustomerTools(
                customer_id=customer.customer_id,
                serial_number="SN-1",
                fab_number="FAB-9",
                model_info="Torque wrench",
                unit_id=unit.id,
            )
        )
        session.commit()

        pricing_response = app.test_client().get("/reports/customers/pricing")
        tools_response = app.test_client().get("/reports/customers/tools-inventory")

        assert pricing_response.status_code == 200
        assert b"Customer Pricing Report" in pricing_response.data
        assert b"C-100" in pricing_response.data
        assert b"1.25" in pricing_response.data

        assert tools_response.status_code == 200
        assert b"Customer Tools Inventory" in tools_response.data
        assert b"SN-1" in tools_response.data
        assert b"FAB-9" in tools_response.data
        assert b"Press" in tools_response.data
    finally:
        session.close()
