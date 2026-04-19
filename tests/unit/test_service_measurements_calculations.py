import pytest
from ith_webapp.models.service_sub import ServiceSub
from ith_webapp.models.service_measurements import ServiceMeasurements
from sqlalchemy.orm import Session

def test_item_sum_and_labor_sum(session: Session):
    # Setup: create ServiceMeasurements and related ServiceSub entries
    sm = ServiceMeasurements(service_id=1)
    session.add(sm)
    session.commit()

    # Add item and labor ServiceSub entries
    item1 = ServiceSub(service_id=1, item_type='I', quantity=2, price=10.0, cost=7.5)
    item2 = ServiceSub(service_id=1, item_type='I', quantity=1, price=20.0, cost=15.0)
    labor1 = ServiceSub(service_id=1, item_type='L', quantity=3, price=30.0, cost=25.0)
    session.add_all([item1, item2, labor1])
    session.commit()

    # The following methods do not exist yet and should fail (Red phase)
    assert sm.item_sum(session) == 7.5 + 15.0
    assert sm.labor_sum(session) == 25.0
