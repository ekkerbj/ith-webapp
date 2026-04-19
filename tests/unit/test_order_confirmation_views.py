from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.models.order_confirmation import OrderConfirmation


def _create_test_app_with_order_confirmations():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.commit()
    session.add(
        OrderConfirmation(
            customer_id=customer.customer_id,
            order_number="OC-1001",
            notes="Confirmed by phone",
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_order_confirmation_list_and_detail_render_confirmation_data():
    app = _create_test_app_with_order_confirmations()
    client = app.test_client()

    list_response = client.get("/order-confirmations/")
    assert list_response.status_code == 200
    list_html = list_response.get_data(as_text=True)
    assert "OC-1001" in list_html

    detail_response = client.get("/order-confirmations/1")
    assert detail_response.status_code == 200
    detail_html = detail_response.get_data(as_text=True)
    assert "OC-1001" in detail_html
    assert "Confirmed by phone" in detail_html


def test_order_confirmation_create_edit_and_delete_routes_work():
    app = _create_test_app_with_order_confirmations()
    client = app.test_client()

    create_response = client.post(
        "/order-confirmations/new",
        data={
            "customer_id": "1",
            "order_number": "OC-2002",
            "notes": "New confirmation",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 302

    edit_response = client.post(
        "/order-confirmations/1/edit",
        data={
            "customer_id": "1",
            "order_number": "OC-1001A",
            "notes": "Updated confirmation",
        },
        follow_redirects=False,
    )
    assert edit_response.status_code == 302

    delete_response = client.post("/order-confirmations/1/delete", follow_redirects=False)
    assert delete_response.status_code == 302
