from sqlalchemy.orm import Session

from ith_webapp.models.customer import Customer
from ith_webapp.repositories.customer_repository import CustomerRepository


def test_find_by_id_returns_customer(session: Session):
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.commit()

    repo = CustomerRepository(session)
    result = repo.find_by_id(customer.customer_id)

    assert result is not None
    assert result.customer_name == "Acme Corp"


def test_find_by_id_returns_none_when_not_found(session: Session):
    repo = CustomerRepository(session)
    result = repo.find_by_id(9999)

    assert result is None


def test_find_all_returns_all_customers(session: Session):
    session.add(Customer(customer_name="Acme Corp", active=True))
    session.add(Customer(customer_name="Beta Inc", active=True))
    session.commit()

    repo = CustomerRepository(session)
    results = repo.find_all()

    assert len(results) == 2


def test_save_persists_new_customer(session: Session):
    repo = CustomerRepository(session)
    customer = Customer(customer_name="New Corp", card_code="C20001", active=True)

    repo.save(customer)

    result = session.get(Customer, customer.customer_id)
    assert result is not None
    assert result.customer_name == "New Corp"
