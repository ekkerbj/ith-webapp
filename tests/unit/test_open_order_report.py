from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.repositories.sap_repository import SapOrderRecord


class _OpenOrderRepository:
    def __init__(self):
        self.card_code = None

    def list_open_orders(self, card_code: str):
        self.card_code = card_code
        return [
            SapOrderRecord(
                doc_entry=101,
                doc_num=2001,
                card_code=card_code,
                total=Decimal("49.99"),
            )
        ]


def _create_app_with_open_order_data():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(Customer(customer_name="Acme Corp", card_code="C10001", active=True))
    session.commit()
    session.close()

    repo = _OpenOrderRepository()
    app.config["SESSION_FACTORY"] = factory
    app.config["SAP_ORDER_REPOSITORY"] = repo
    return app, repo


def test_open_order_report_shows_customer_open_orders():
    app, repo = _create_app_with_open_order_data()

    response = app.test_client().get("/reports/open-order/1")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Open Order Report" in body
    assert "Acme Corp" in body
    assert "2001" in body
    assert "49.99" in body
    assert repo.card_code == "C10001"
