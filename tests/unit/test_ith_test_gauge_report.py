from sqlalchemy.orm import Session

from ith_webapp.models import ITHTestGauge, ITHTestGaugeType
from ith_webapp.reports import build_ith_test_gauge_certificates_pdf


def test_build_ith_test_gauge_certificates_pdf_includes_certificate_titles_and_gauge_data(
    session: Session,
):
    gauge_type = ITHTestGaugeType(name="Micrometer")
    session.add(gauge_type)
    session.flush()

    gauge = ITHTestGauge(
        ith_test_gauge_type_id=gauge_type.ith_test_gauge_type_id,
        name="Gauge A",
        serial_number="TG-001",
        calibration_due_date=None,
        certification_due_date=None,
    )
    session.add(gauge)
    session.commit()

    pdf_bytes = build_ith_test_gauge_certificates_pdf(session, gauge.ith_test_gauge_id, variant="iso17025")

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Gauge Calibration Certificate" in pdf_bytes
    assert b"Force Test Certificate" in pdf_bytes
    assert b"Torque Test Certificate" in pdf_bytes
    assert b"ISO 17025" in pdf_bytes
    assert b"Gauge A" in pdf_bytes
    assert b"TG-001" in pdf_bytes
    assert b"Micrometer" in pdf_bytes


def test_ith_test_gauge_certificate_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        gauge_type = ITHTestGaugeType(name="Micrometer")
        session.add(gauge_type)
        session.flush()

        gauge = ITHTestGauge(
            ith_test_gauge_type_id=gauge_type.ith_test_gauge_type_id,
            name="Gauge A",
            serial_number="TG-001",
        )
        session.add(gauge)
        session.commit()

        response = app.test_client().get(
            f"/reports/ith-test-gauge-certificates/{gauge.ith_test_gauge_id}?variant=iso17025"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
