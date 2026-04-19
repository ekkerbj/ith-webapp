from sqlalchemy.orm import Session
import pytest

from ith_webapp.models.customer import Customer
# Market and CustomerMarket will be imported after implementation

from ith_webapp.models.market import Market
from ith_webapp.models.customer_market import CustomerMarket

def test_customer_can_be_assigned_to_market(session: Session):
    # Arrange: create customer and market
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    market = Market(name="Industrial")
    session.add_all([customer, market])
    session.commit()

    # Act: assign customer to market (CustomerMarket association)
    customer.markets.append(market)
    session.commit()

    # Assert: customer is associated with market
    refreshed_customer = session.get(Customer, customer.customer_id)
    assert market in refreshed_customer.markets
