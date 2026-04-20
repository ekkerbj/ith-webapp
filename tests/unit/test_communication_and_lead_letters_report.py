from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models import (
    Customer,
    CustomerCommunicationLog,
    WindTurbineLead,
    WindTurbineLeadDetail,
)


def _create_test_app():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    app.config["SESSION_FACTORY"] = sessionmaker(bind=engine)
    return app


def test_customer_communication_report_route_returns_pdf_with_logs_in_order():
    app = _create_test_app()
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        customer = Customer(customer_name="Acme", card_code="C-100")
        session.add(customer)
        session.flush()
        session.add_all(
            [
                CustomerCommunicationLog(
                    customer_id=customer.customer_id,
                    note="Initial call",
                    created_at=datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc),
                ),
                CustomerCommunicationLog(
                    customer_id=customer.customer_id,
                    note="Follow-up email",
                    created_at=datetime(2026, 1, 6, 15, 30, tzinfo=timezone.utc),
                ),
            ]
        )
        session.commit()

        response = app.test_client().get(
            f"/reports/customer-communications/{customer.customer_id}"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
        assert b"Customer Communication Report" in response.data
        assert b"Acme" in response.data
        assert b"Initial call" in response.data
        assert b"Follow-up email" in response.data
        assert response.data.index(b"Initial call") < response.data.index(b"Follow-up email")
    finally:
        session.close()


def test_wind_turbine_lead_letter_route_returns_pdf_with_lead_notes():
    app = _create_test_app()
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        lead = WindTurbineLead(
            customer_name="Acme",
            contact_name="Jordan Smith",
            phone="555-0100",
            email="jordan@example.com",
            status="New",
            notes="Interested in a wind turbine quote",
        )
        session.add(lead)
        session.flush()
        session.add(
            WindTurbineLeadDetail(
                wind_turbine_lead_id=lead.wind_turbine_lead_id,
                notes="Called back for follow-up",
            )
        )
        session.commit()

        response = app.test_client().get(
            f"/reports/wind-turbine-leads/{lead.wind_turbine_lead_id}/letter"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
        assert b"Wind Turbine Lead Letter" in response.data
        assert b"Acme" in response.data
        assert b"Jordan Smith" in response.data
        assert b"Called back for follow-up" in response.data
    finally:
        session.close()


def test_wind_turbine_lead_follow_up_letter_route_returns_pdf_for_selected_detail():
    app = _create_test_app()
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        lead = WindTurbineLead(
            customer_name="Acme",
            contact_name="Jordan Smith",
            phone="555-0100",
            email="jordan@example.com",
            status="Working",
            notes="Interested in a site visit",
        )
        session.add(lead)
        session.flush()
        first_detail = WindTurbineLeadDetail(
            wind_turbine_lead_id=lead.wind_turbine_lead_id,
            notes="Left voicemail",
        )
        second_detail = WindTurbineLeadDetail(
            wind_turbine_lead_id=lead.wind_turbine_lead_id,
            notes="Scheduled follow-up call",
        )
        session.add_all([first_detail, second_detail])
        session.commit()

        response = app.test_client().get(
            f"/reports/wind-turbine-leads/{lead.wind_turbine_lead_id}/follow-up-letter/{second_detail.wind_turbine_lead_detail_id}"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
        assert b"Wind Turbine Lead Follow-Up Letter" in response.data
        assert b"Scheduled follow-up call" in response.data
    finally:
        session.close()
