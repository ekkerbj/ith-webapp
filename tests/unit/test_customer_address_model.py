from sqlalchemy.orm import Session
import pytest

from ith_webapp.models.customer import Customer
# CustomerAddress will be imported after implementation

@pytest.mark.skip("CustomerAddress model not implemented yet")
def test_customer_address_can_be_persisted_and_retrieved(session: Session):
    # This test will fail until CustomerAddress model exists
    from ith_webapp.models.customer_address import CustomerAddress
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.commit()

    address = CustomerAddress(
        customer_id=customer.customer_id,
        address_type="Billing",
        street="123 Main St",
        city="Metropolis",
        state="NY",
        zip_code="12345",
        country="USA",
    )
    session.add(address)
    session.commit()

    result = session.get(CustomerAddress, address.address_id)
    assert result is not None
    assert result.customer_id == customer.customer_id
    assert result.address_type == "Billing"
    assert result.street == "123 Main St"
    assert result.city == "Metropolis"
    assert result.state == "NY"
    assert result.zip_code == "12345"
    assert result.country == "USA"
