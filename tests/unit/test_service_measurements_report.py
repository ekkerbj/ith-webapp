from sqlalchemy.orm import Session

from ith_webapp.models import Customer, Service, ServiceMeasurements
from ith_webapp.reports import build_service_measurements_pdf


def test_build_service_measurements_pdf_includes_tool_reports(session: Session):
    customer = Customer(customer_name="Acme Services", active=True)
    session.add(customer)
    session.flush()

    service = Service(customer_id=customer.customer_id, cardcode="C-100")
    session.add(service)
    session.flush()

    measurements = ServiceMeasurements(
        service_id=service.service_id,
        btc_passed=True,
        gauge_value=1.23,
        hose_pressure=2.34,
        nut_runner_torque=3.45,
        pump_output=4.56,
        torque_wrench_setting=5.67,
    )
    session.add(measurements)
    session.commit()

    pdf_bytes = build_service_measurements_pdf(session, service.service_id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"BTC Measurement Form" in pdf_bytes
    assert b"BTC Test Report" in pdf_bytes
    assert b"Gauge Measurement Form" in pdf_bytes
    assert b"Hose Test Report" in pdf_bytes
    assert b"Torque Wrench Measurement Form" in pdf_bytes
    assert b"Acme Services" in pdf_bytes
    assert b"1.23" in pdf_bytes
    assert b"5.67" in pdf_bytes


def test_service_measurements_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Route Customer", active=True)
        session.add(customer)
        session.flush()

        service = Service(customer_id=customer.customer_id, cardcode="C-200")
        session.add(service)
        session.flush()

        session.add(ServiceMeasurements(service_id=service.service_id, btc_passed=False))
        session.commit()

        response = app.test_client().get(
            f"/reports/service-measurements/{service.service_id}"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
