from sqlalchemy.orm import Session

from ith_webapp.models import Customer, Service, ServiceSub
from ith_webapp.reports import build_service_multi_quote_pdf


def test_build_service_multi_quote_pdf_includes_sections_and_region(session: Session):
    customer = Customer(customer_name="Acme")
    session.add(customer)
    session.flush()

    service = Service(
        customer_id=customer.customer_id,
        cardcode="C123",
        order_status="Quoted",
        sale_type="Repair",
        technician="Tech1",
        price=100.0,
        cost=50.0,
        active=True,
    )
    session.add(service)
    session.flush()

    session.add_all(
        [
            ServiceSub(service_id=service.service_id, item_type="F", quantity=1, price=100.0, cost=80.0),
            ServiceSub(service_id=service.service_id, item_type="A", quantity=2, price=20.0, cost=15.0),
            ServiceSub(service_id=service.service_id, item_type="S", quantity=1, price=50.0, cost=40.0),
        ]
    )
    session.commit()

    pdf_bytes = build_service_multi_quote_pdf(session, service.service_id, region="BR")

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Service Multi Quote" in pdf_bytes
    assert b"Brazil" in pdf_bytes
    assert b"-BR" in pdf_bytes
    assert b"Fab Number Line Items" in pdf_bytes
    assert b"Accessories" in pdf_bytes
    assert b"Sales Items" in pdf_bytes
    assert b"Signature" in pdf_bytes


def test_service_multi_quote_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme")
        session.add(customer)
        session.flush()

        service = Service(
            customer_id=customer.customer_id,
            cardcode="C123",
            order_status="Quoted",
            sale_type="Repair",
            technician="Tech1",
            price=100.0,
            cost=50.0,
            active=True,
        )
        session.add(service)
        session.flush()

        session.add(
            ServiceSub(
                service_id=service.service_id,
                item_type="F",
                quantity=1,
                price=100.0,
                cost=80.0,
            )
        )
        session.commit()

        response = app.test_client().get(
            f"/reports/service-multi-quote/{service.service_id}?region=MX"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
