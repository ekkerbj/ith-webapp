from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models import Customer, CustomerContact


def _create_test_app():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    app.config["SESSION_FACTORY"] = sessionmaker(bind=engine)
    return app


def test_names_report_route_returns_pdf_with_customer_contacts():
    app = _create_test_app()
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme Corp", card_code="C-100")
        session.add(customer)
        session.flush()
        session.add_all(
            [
                CustomerContact(
                    customer_id=customer.customer_id,
                    name="Jane Doe",
                    email="jane@example.com",
                    phone="555-1000",
                    position="Manager",
                ),
                CustomerContact(
                    customer_id=customer.customer_id,
                    name="John Smith",
                    email="john@example.com",
                    phone="555-2000",
                    position="Assistant",
                ),
            ]
        )
        session.commit()

        response = app.test_client().get("/reports/names")

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
        assert b"Names" in response.data
        assert b"Acme Corp" in response.data
        assert b"Jane Doe" in response.data
        assert b"John Smith" in response.data
    finally:
        session.close()


def test_credit_card_authorization_form_route_returns_pdf():
    app = _create_test_app()

    response = app.test_client().get("/reports/credit-card-authorization-form")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")
    assert b"Credit Card Authorization Form" in response.data
    assert b"Signature" in response.data
    assert b"Date" in response.data
