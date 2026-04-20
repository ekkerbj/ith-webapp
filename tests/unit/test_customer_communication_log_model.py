import pytest
from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_communication_log import CustomerCommunicationLog
import pytest

def test_create_communication_log(session):
    customer = Customer(customer_name="Test Customer")
    session.add(customer)
    session.commit()
    log = CustomerCommunicationLog(customer_id=customer.customer_id, note="Called customer.")
    session.add(log)
    session.commit()
    retrieved = session.query(CustomerCommunicationLog).filter_by(customer_id=customer.customer_id).first()
    assert retrieved is not None
    assert retrieved.note == "Called customer."
