from sqlalchemy.orm import Session
import pytest

from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_contact import CustomerContact


def test_customer_contact_can_be_persisted_and_retrieved(session: Session):
    customer = Customer(
        customer_name="Acme Corp",
        card_code="C10001",
        active=True,
    )
    session.add(customer)
    session.commit()

    contact = CustomerContact(
        customer_id=customer.customer_id,
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        position="Manager"
    )
    session.add(contact)
    session.commit()

    result = session.get(CustomerContact, contact.contact_id)
    assert result is not None
    assert result.customer_id == customer.customer_id
    assert result.name == "John Doe"
    assert result.email == "john@example.com"
    assert result.phone == "555-1234"
    assert result.position == "Manager"
