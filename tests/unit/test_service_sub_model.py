import pytest
from ith_webapp.models import Service
from ith_webapp.database import Base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

from ith_webapp.models.service import Service
# ServiceSub does not exist yet, this test should fail (Red phase)
def test_create_service_sub(session):
    from ith_webapp.models.service_sub import ServiceSub
    service_sub = ServiceSub(
        service_id=1,
        item_type='I',
        quantity=2,
        price=10.0,
        cost=7.5
    )
    session.add(service_sub)
    session.commit()
    result = session.query(ServiceSub).first()
    assert result is not None
    assert result.item_type == 'I'
    assert result.quantity == 2
    assert result.price == 10.0
    assert result.cost == 7.5
