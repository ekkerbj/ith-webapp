from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_address import CustomerAddress


def _create_test_app_with_customers(*customers):
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    for customer in customers:
        session.add(customer)
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_customer_mailing_labels_route_renders_customer_addresses():
    app = _create_test_app_with_customers(
        Customer(customer_name="Acme Corp", card_code="C10001", active=True),
    )
    session = app.config["SESSION_FACTORY"]()
    session.add(
        CustomerAddress(
            customer_id=1,
            address_type="Billing",
            street="123 Main St",
            city="Metropolis",
            state="NY",
            zip_code="12345",
            country="USA",
        )
    )
    session.commit()
    session.close()

    client = app.test_client()

    response = client.get("/customers/labels/mailing?format=single")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Mailing Labels" in html
    assert "Acme Corp" in html
    assert "123 Main St" in html


def test_customer_mailing_labels_route_uses_guided_header():
    app = _create_test_app_with_customers(
        Customer(customer_name="Acme Corp", card_code="C10001", active=True),
    )
    client = app.test_client()

    response = client.get("/customers/labels/mailing?format=single")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Label sheet" in html
    assert "Print-ready customer labels" in html


def test_customer_address_labels_route_renders_multi_label_layout():
    app = _create_test_app_with_customers(
        Customer(customer_name="Acme Corp", card_code="C10001", active=True),
    )
    session = app.config["SESSION_FACTORY"]()
    session.add(
        CustomerAddress(
            customer_id=1,
            address_type="Shipping",
            street="456 Oak Ave",
            city="Star City",
            state="CA",
            zip_code="90210",
            country="USA",
        )
    )
    session.commit()
    session.close()

    client = app.test_client()

    response = client.get("/customers/labels/address?format=multi")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Address Labels" in html
    assert "Shipping" in html
    assert "customer-label-sheet--multi" in html


def test_customer_sap_address_labels_route_renders_sap_variant():
    app = _create_test_app_with_customers(
        Customer(customer_name="Acme Corp", card_code="C10001", active=True),
    )
    session = app.config["SESSION_FACTORY"]()
    session.add(
        CustomerAddress(
            customer_id=1,
            address_type="SAP",
            street="789 Pine Rd",
            city="Central City",
            state="IL",
            zip_code="60601",
            country="USA",
        )
    )
    session.commit()
    session.close()

    client = app.test_client()

    response = client.get("/customers/labels/sap")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "SAP Address Labels" in html
    assert "SAP Address Label" in html
    assert "789 Pine Rd" in html
