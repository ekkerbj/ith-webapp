from sqlalchemy.orm import Session

from ith_webapp.models import ConsignmentList, Customer, Part, Service, ServiceSub
from ith_webapp.reports import build_customer_parts_list_pdf, build_service_multi_quote_pdf


def test_build_service_multi_quote_pdf_uses_alstom_variant(session: Session):
    customer = Customer(customer_name="Alstom Wind Energy")
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
    session.add(ServiceSub(service_id=service.service_id, item_type="F", quantity=1, price=100.0, cost=80.0))
    session.commit()

    pdf_bytes = build_service_multi_quote_pdf(session, service.service_id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Alstom Multi Quote" in pdf_bytes


def test_build_customer_parts_list_pdf_uses_mortenson_variant(session: Session):
    customer = Customer(customer_name="Mortenson Construction", card_code="M100")
    part = Part(part_number="P-9001", description="Legacy part", active=True)
    session.add_all([customer, part])
    session.flush()
    session.add(ConsignmentList(customer_id=customer.customer_id, part_id=part.part_id, quantity=4))
    session.commit()

    pdf_bytes = build_customer_parts_list_pdf(session, customer.customer_id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Mortenson Part Pics" in pdf_bytes

