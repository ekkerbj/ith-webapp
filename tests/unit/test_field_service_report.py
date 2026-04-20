from sqlalchemy.orm import Session

from ith_webapp.models import (
    Customer,
    FieldService,
    FieldServiceStatus,
    Service,
    ServiceTime,
)
from ith_webapp.reports import (
    build_field_service_report_pdf,
    build_field_service_summary_pdf,
    build_field_service_timesheet_pdf,
)


def test_build_field_service_reports_pdf_includes_customer_and_time_data(
    session: Session,
):
    customer = Customer(customer_name="Acme Field Services", active=True)
    status = FieldServiceStatus(name="Complete")
    session.add_all([customer, status])
    session.flush()

    field_service = FieldService(
        customer_id=customer.customer_id,
        field_service_status_id=status.field_service_status_id,
        visit_notes="Installed replacement assembly",
    )
    session.add(field_service)
    session.flush()

    service = Service(
        customer_id=customer.customer_id,
        technician="Tech One",
        price=250.0,
        cost=125.0,
        active=True,
    )
    session.add(service)
    session.flush()

    session.add(
        ServiceTime(
            service_id=service.service_id,
            technician="Tech One",
            hours=2.5,
            date="2026-04-19",
            labor_rate=125.0,
        )
    )
    session.commit()

    report_pdf = build_field_service_report_pdf(session, field_service.field_service_id)
    summary_pdf = build_field_service_summary_pdf(session, field_service.field_service_id)
    timesheet_pdf = build_field_service_timesheet_pdf(
        session, field_service.field_service_id, customer_facing=True
    )

    assert report_pdf.startswith(b"%PDF")
    assert b"Field Service Report" in report_pdf
    assert b"Acme Field Services" in report_pdf
    assert b"Complete" in report_pdf
    assert b"Installed replacement assembly" in report_pdf
    assert summary_pdf.startswith(b"%PDF")
    assert b"Field Service Summary" in summary_pdf
    assert b"Timesheet" in timesheet_pdf
    assert b"Customer-facing Timesheet" in timesheet_pdf
    assert b"Tech One" in timesheet_pdf
    assert b"2.5" in timesheet_pdf


def test_field_service_report_routes_return_pdfs(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Route Field Services", active=True)
        status = FieldServiceStatus(name="Open")
        session.add_all([customer, status])
        session.flush()

        field_service = FieldService(
            customer_id=customer.customer_id,
            field_service_status_id=status.field_service_status_id,
            visit_notes="Route coverage",
        )
        session.add(field_service)
        session.flush()

        service = Service(customer_id=customer.customer_id, technician="Route Tech", active=True)
        session.add(service)
        session.flush()

        session.add(
            ServiceTime(
                service_id=service.service_id,
                technician="Route Tech",
                hours=1.0,
                date="2026-04-19",
                labor_rate=99.0,
            )
        )
        session.commit()

        client = app.test_client()
        report_response = client.get(f"/reports/field-service/{field_service.field_service_id}")
        summary_response = client.get(
            f"/reports/field-service-summary/{field_service.field_service_id}"
        )
        timesheet_response = client.get(
            f"/reports/field-service-timesheet/{field_service.field_service_id}?customer_facing=1"
        )

        assert report_response.status_code == 200
        assert report_response.mimetype == "application/pdf"
        assert report_response.data.startswith(b"%PDF")
        assert summary_response.status_code == 200
        assert summary_response.mimetype == "application/pdf"
        assert timesheet_response.status_code == 200
        assert timesheet_response.mimetype == "application/pdf"
    finally:
        session.close()
