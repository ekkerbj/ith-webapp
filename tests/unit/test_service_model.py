import pytest
from datetime import datetime
from ith_webapp.models import Service
from ith_webapp.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

def test_create_service(session):
    service = Service(
        customer_id=1,
        cardcode="C123",
        order_status="Open",
        sale_type="Repair",
        technician="Tech1",
        price=100.0,
        cost=50.0,
        active=True
    )
    session.add(service)
    session.commit()
    result = session.query(Service).first()
    assert result is not None
    assert result.cardcode == "C123"
    assert result.order_status == "Open"
    assert result.technician == "Tech1"
    assert result.price == 100.0
    assert result.cost == 50.0
    assert result.active is True

def test_create_service_time(session):
    # ServiceTime does not exist yet, this test should fail (Red phase)
    from ith_webapp.models.service_time import ServiceTime
    service_time = ServiceTime(
        service_id=1,
        technician="Tech1",
        hours=2.5,
        date="2026-04-19",
        labor_rate=45.0
    )
    session.add(service_time)
    session.commit()
    result = session.query(ServiceTime).first()
    assert result is not None
    assert result.technician == "Tech1"
    assert result.hours == 2.5
    assert result.date == "2026-04-19"
    assert result.labor_rate == 45.0


def test_service_persists_extended_fields(session):
    service = Service(
        customer_id=1,
        cardcode="C123",
        order_status="Open",
        sale_type="Repair",
        technician="Lead Tech",
        price=100.0,
        cost=50.0,
        active=True,
        received_date=datetime(2026, 4, 1, 8, 30),
        quoted_date=datetime(2026, 4, 2, 9, 0),
        completed_date=datetime(2026, 4, 8, 16, 45),
        customer_po="PO-100",
        invoice_number="INV-200",
        work_order_number="WO-300",
        assigned_technician="Lead Tech",
        secondary_technician="Assist Tech",
        customer_notes="Customer wants afternoon delivery.",
        internal_notes="Verify torque settings before release.",
        tracking_number="1Z999",
        ship_via="Ground",
        quote_status="Quoted",
    )
    session.add(service)
    session.commit()

    result = session.query(Service).first()

    assert result is not None
    assert result.customer_po == "PO-100"
    assert result.invoice_number == "INV-200"
    assert result.assigned_technician == "Lead Tech"
