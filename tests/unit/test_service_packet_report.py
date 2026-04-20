from sqlalchemy.orm import Session

from ith_webapp.models import Customer, ITHTestGauge, ITHTestGaugeType, Service, ServiceMeasurements
from ith_webapp.reports import build_service_packet_pdf


def test_build_service_packet_pdf_combines_service_reports(session: Session):
    customer = Customer(customer_name="Acme Services", active=True)
    session.add(customer)
    session.flush()

    service = Service(customer_id=customer.customer_id, cardcode="C-100")
    session.add(service)
    session.flush()

    gauge_type = ITHTestGaugeType(name="Micrometer")
    session.add(gauge_type)
    session.flush()

    gauge = ITHTestGauge(
        ith_test_gauge_type_id=gauge_type.ith_test_gauge_type_id,
        name="Gauge A",
        serial_number="TG-001",
    )
    session.add(gauge)
    session.add(
        ServiceMeasurements(
            service_id=service.service_id,
            btc_passed=True,
            gauge_value=1.23,
        )
    )
    session.commit()

    pdf_bytes = build_service_packet_pdf(
        session,
        service.service_id,
        ith_test_gauge_id=gauge.ith_test_gauge_id,
    )

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Service Packet" in pdf_bytes
    assert b"Service Multi Quote" in pdf_bytes
    assert b"BTC Measurement Form" in pdf_bytes
    assert b"Gauge Calibration Certificate" in pdf_bytes


def test_service_packet_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme Services", active=True)
        session.add(customer)
        session.flush()

        service = Service(customer_id=customer.customer_id, cardcode="C-100")
        session.add(service)
        session.flush()

        gauge_type = ITHTestGaugeType(name="Micrometer")
        session.add(gauge_type)
        session.flush()

        gauge = ITHTestGauge(
            ith_test_gauge_type_id=gauge_type.ith_test_gauge_type_id,
            name="Gauge A",
            serial_number="TG-001",
        )
        session.add(gauge)
        session.add(ServiceMeasurements(service_id=service.service_id, btc_passed=True))
        session.commit()

        response = app.test_client().get(
            f"/reports/service-packet/{service.service_id}?gauge_id={gauge.ith_test_gauge_id}"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
