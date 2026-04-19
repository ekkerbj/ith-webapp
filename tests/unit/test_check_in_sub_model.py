import pytest
from sqlalchemy.orm import Session
from ith_webapp.models import Customer, CheckIn

# Failing test for CheckInSub model and workflow (F-013)
def test_check_in_sub_can_be_persisted_and_retrieved(session: Session):
    # This will fail until CheckInSub model is implemented
    from ith_webapp.models import CheckInSub  # noqa: F401
    customer = Customer(customer_name="Test Customer")
    session.add(customer)
    session.commit()
    check_in = CheckIn(customer_id=customer.customer_id, description="Test check-in")
    session.add(check_in)
    session.commit()
    check_in_sub = CheckInSub(check_in_id=check_in.id, tool_id=1, inspected=False, quoted=False, approved=False, closed=False)
    session.add(check_in_sub)
    session.commit()
    result = session.get(CheckInSub, check_in_sub.id)
    assert result is not None
    assert result.check_in_id == check_in.id
    assert result.inspected is False
    assert result.quoted is False
    assert result.approved is False
    assert result.closed is False
