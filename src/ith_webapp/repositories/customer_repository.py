from sqlalchemy import select
from sqlalchemy.orm import Session

from ith_webapp.models.customer import Customer


class CustomerRepository:
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, customer_id: int) -> Customer | None:
        return self._session.get(Customer, customer_id)

    def find_all(self) -> list[Customer]:
        stmt = select(Customer)
        return list(self._session.scalars(stmt).all())

    def save(self, customer: Customer) -> None:
        self._session.add(customer)
        self._session.commit()
