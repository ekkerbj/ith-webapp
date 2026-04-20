from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer


def test_customer_list_paginates_results():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add_all(
        [
            Customer(customer_name="Acme Corp", card_code="C10001", active=True),
            Customer(customer_name="Beta Inc", card_code="B20002", active=True),
            Customer(customer_name="Gamma LLC", card_code="G30003", active=True),
        ]
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    client = app.test_client()

    response = client.get("/customers/?page=2&page_size=1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Beta Inc" in html
    assert "Acme Corp" not in html
    assert "Gamma LLC" not in html
    assert "Page 2 of 3" in html
