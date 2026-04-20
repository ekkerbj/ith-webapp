from sqlalchemy.orm import Session

from ith_webapp.models import CheckIn, CheckInSub, Customer
from ith_webapp.reports import build_check_in_pdf


def test_build_check_in_pdf_includes_tools_and_customer(session: Session):
    customer = Customer(customer_name="Acme")
    session.add(customer)
    session.flush()

    check_in = CheckIn(customer_id=customer.customer_id, description="Tool receipt")
    session.add(check_in)
    session.flush()

    session.add(
        CheckInSub(
            check_in_id=check_in.id,
            tool_id=42,
            inspected=True,
            quoted=False,
            approved=True,
            closed=False,
        )
    )
    session.commit()

    pdf_bytes = build_check_in_pdf(session, check_in.id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Check In Document" in pdf_bytes
    assert b"Tool Receipt" in pdf_bytes
    assert b"Tools Received" in pdf_bytes
    assert b"Acme" in pdf_bytes
    assert b"42" in pdf_bytes


def test_check_in_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme")
        session.add(customer)
        session.flush()

        check_in = CheckIn(customer_id=customer.customer_id, description="Tool receipt")
        session.add(check_in)
        session.flush()

        session.add(CheckInSub(check_in_id=check_in.id, tool_id=42))
        session.commit()

        response = app.test_client().get(f"/reports/check-in/{check_in.id}")

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
