from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.models.field_service import FieldService
from ith_webapp.models.field_service_status import FieldServiceStatus


def _create_test_app_with_field_services():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    status = FieldServiceStatus(name="Open")
    session.add(customer)
    session.add(status)
    session.commit()
    session.add(
        FieldService(
            customer_id=customer.customer_id,
            field_service_status_id=status.field_service_status_id,
            visit_notes="On-site visit",
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_field_service_list_renders_items():
    app = _create_test_app_with_field_services()
    client = app.test_client()

    response = client.get("/field-services/")

    assert response.status_code == 200


def test_field_service_list_filters_by_customer_status_or_id():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer_one = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    customer_two = Customer(customer_name="Beta Inc", card_code="B20002", active=True)
    open_status = FieldServiceStatus(name="Open")
    closed_status = FieldServiceStatus(name="Closed")
    session.add_all([customer_one, customer_two, open_status, closed_status])
    session.commit()
    session.add(
        FieldService(
            customer_id=customer_one.customer_id,
            field_service_status_id=open_status.field_service_status_id,
            visit_notes="On-site visit",
        )
    )
    session.add(
        FieldService(
            customer_id=customer_two.customer_id,
            field_service_status_id=closed_status.field_service_status_id,
            visit_notes="Closed visit",
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    client = app.test_client()

    response = client.get("/field-services/?q=closed")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Beta Inc" in html
    assert "Acme Corp" not in html


def test_field_service_detail_renders_fields():
    app = _create_test_app_with_field_services()
    client = app.test_client()

    response = client.get("/field-services/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Acme Corp" in html
    assert "Open" in html
    assert "On-site visit" in html


def test_field_service_create_saves_and_redirects():
    app = _create_test_app_with_field_services()
    client = app.test_client()

    response = client.post(
        "/field-services/new",
        data={
            "customer_id": "1",
            "field_service_status_id": "1",
            "visit_notes": "New visit",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/field-services/" in response.headers["Location"]


def test_field_service_edit_updates_and_redirects():
    app = _create_test_app_with_field_services()
    client = app.test_client()

    response = client.post(
        "/field-services/1/edit",
        data={
            "customer_id": "1",
            "field_service_status_id": "1",
            "visit_notes": "Updated visit",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/field-services/1" in response.headers["Location"]


def test_field_service_delete_removes_item():
    app = _create_test_app_with_field_services()
    client = app.test_client()

    response = client.post("/field-services/1/delete", follow_redirects=False)

    assert response.status_code == 302
    assert "/field-services/" in response.headers["Location"]
