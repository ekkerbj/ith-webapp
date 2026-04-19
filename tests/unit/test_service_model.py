import pytest
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
