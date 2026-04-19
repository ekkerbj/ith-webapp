from sqlalchemy.orm import Session

from ith_webapp.models.customer import Customer


def test_customer_can_be_persisted_and_retrieved(session: Session):
    customer = Customer(
        customer_name="Acme Corp",
        card_code="C10001",
        active=True,
    )
    session.add(customer)
    session.commit()

    result = session.get(Customer, customer.customer_id)

    assert result is not None
    assert result.customer_name == "Acme Corp"
    assert result.card_code == "C10001"
    assert result.active is True
