from sqlalchemy.orm import Session

from ith_webapp.models import Customer, CustomerTools, CustomerToolsSub, Unit
from ith_webapp.reports import build_customer_tools_pdf


def test_build_customer_tools_pdf_includes_tool_details_and_components(session: Session):
    customer = Customer(customer_name="Acme Services", active=True)
    unit = Unit(name="Hydraulic")
    session.add_all([customer, unit])
    session.flush()

    tool = CustomerTools(
        customer_id=customer.customer_id,
        serial_number="SN-1001",
        fab_number="FAB-9",
        model_info="Model X",
        unit_id=unit.id,
    )
    session.add(tool)
    session.flush()
    session.add_all(
        [
            CustomerToolsSub(tool_id=tool.id, sub_type="Pump", value="Installed"),
            CustomerToolsSub(tool_id=tool.id, sub_type="Gauge", value="Calibrated"),
        ]
    )
    session.commit()

    pdf_bytes = build_customer_tools_pdf(session, tool.id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Toolset Detail Report" in pdf_bytes
    assert b"Acme Services" in pdf_bytes
    assert b"SN-1001" in pdf_bytes
    assert b"FAB-9" in pdf_bytes
    assert b"Model X" in pdf_bytes
    assert b"Component List" in pdf_bytes
    assert b"Pump" in pdf_bytes
    assert b"Gauge" in pdf_bytes


def test_customer_tools_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Route Customer", active=True)
        session.add(customer)
        session.flush()

        tool = CustomerTools(customer_id=customer.customer_id, serial_number="SN-2002")
        session.add(tool)
        session.commit()

        response = app.test_client().get(f"/reports/customer-tools/{tool.id}")

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
