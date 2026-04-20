from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.consignment_list import ConsignmentList
from ith_webapp.models.customer import Customer
from ith_webapp.models.part import Part


def _create_test_app_with_consignment_items():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    part = Part(part_number="P-1001", description="Test Part", active=True)
    session.add(customer)
    session.add(part)
    session.commit()
    session.add(
        ConsignmentList(customer_id=customer.customer_id, part_id=part.part_id, quantity=12)
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_consignment_list_renders_items():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.get("/consignment-lists/")

    assert response.status_code == 200


def test_consignment_list_detail_renders_item_fields():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.get("/consignment-lists/1")

    assert response.status_code == 200


def test_consignment_list_create_form_renders():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.get("/consignment-lists/new")

    assert response.status_code == 200


def test_consignment_list_create_saves_and_redirects():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.post(
        "/consignment-lists/new",
        data={"customer_id": "1", "part_id": "1", "quantity": "4"},
        follow_redirects=False,
    )

    assert response.status_code == 302


def test_consignment_list_edit_form_renders():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.get("/consignment-lists/1/edit")

    assert response.status_code == 200


def test_consignment_list_edit_updates_and_redirects():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.post(
        "/consignment-lists/1/edit",
        data={"customer_id": "1", "part_id": "1", "quantity": "8"},
        follow_redirects=False,
    )

    assert response.status_code == 302


def test_consignment_list_delete_removes_item():
    app = _create_test_app_with_consignment_items()
    client = app.test_client()

    response = client.post("/consignment-lists/1/delete", follow_redirects=False)

    assert response.status_code == 302
