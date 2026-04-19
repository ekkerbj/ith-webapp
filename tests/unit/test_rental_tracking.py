from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.models.customer_tools import CustomerTools


def _create_test_app_with_rentals():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    tool = CustomerTools(customer=customer, serial_number="SN-1001")
    session.add(customer)
    session.add(tool)
    session.commit()

    from ith_webapp.models.rental import Rental
    from ith_webapp.models.rental_status import RentalStatus

    rental_status = RentalStatus(name="Checked Out")
    session.add(rental_status)
    session.commit()
    session.add(
        Rental(
            customer_id=customer.customer_id,
            customer_tools_id=tool.id,
            rental_status_id=rental_status.rental_status_id,
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_rental_model_persists_required_fields(session):
    from ith_webapp.models.rental import Rental
    from ith_webapp.models.rental_status import RentalStatus

    rental_status = RentalStatus(name="Checked Out")
    session.add(rental_status)
    session.commit()

    rental = Rental(
        customer_id=1,
        customer_tools_id=1,
        rental_status_id=rental_status.rental_status_id,
    )
    session.add(rental)
    session.commit()

    result = session.get(Rental, rental.rental_id)

    assert result is not None
    assert result.rental_status_id == rental_status.rental_status_id


def test_rental_list_and_detail_render_rental_data():
    app = _create_test_app_with_rentals()
    client = app.test_client()

    list_response = client.get("/rentals/")
    assert list_response.status_code == 200
    list_html = list_response.get_data(as_text=True)
    assert "Acme Corp" in list_html
    assert "SN-1001" in list_html
    assert "Checked Out" in list_html

    detail_response = client.get("/rentals/1")
    assert detail_response.status_code == 200
    detail_html = detail_response.get_data(as_text=True)
    assert "Acme Corp" in detail_html
    assert "SN-1001" in detail_html
    assert "Checked Out" in detail_html


def test_rental_create_edit_and_delete_routes_work():
    app = _create_test_app_with_rentals()
    client = app.test_client()

    create_response = client.post(
        "/rentals/new",
        data={
            "customer_id": "1",
            "customer_tools_id": "1",
            "rental_status_id": "1",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 302

    edit_response = client.post(
        "/rentals/1/edit",
        data={
            "customer_id": "1",
            "customer_tools_id": "1",
            "rental_status_id": "1",
        },
        follow_redirects=False,
    )
    assert edit_response.status_code == 302

    delete_response = client.post("/rentals/1/delete", follow_redirects=False)
    assert delete_response.status_code == 302
