import pytest
from sqlalchemy.orm import Session
from ith_webapp.models import Customer, CheckIn

def test_check_in_can_be_persisted_and_retrieved(session: Session):
    customer = Customer(customer_name="Test Customer")
    session.add(customer)
    session.commit()
    check_in = CheckIn(customer_id=customer.customer_id, description="Tool received")
    session.add(check_in)
    session.commit()
    result = session.get(CheckIn, check_in.id)
    assert result is not None
    assert result.customer_id == customer.customer_id
    assert result.description == "Tool received"
