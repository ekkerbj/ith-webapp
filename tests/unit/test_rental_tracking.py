from datetime import date, datetime, timezone

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


def test_rental_list_limits_results_to_the_current_month():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    current_customer = Customer(customer_name="Current Month", card_code="C20001", active=True)
    previous_customer = Customer(customer_name="Previous Month", card_code="C20002", active=True)
    current_tool = CustomerTools(customer=current_customer, serial_number="SN-2001")
    previous_tool = CustomerTools(customer=previous_customer, serial_number="SN-2002")
    session.add_all([current_customer, previous_customer, current_tool, previous_tool])
    session.commit()

    from ith_webapp.models.rental import Rental
    from ith_webapp.models.rental_status import RentalStatus

    rental_status = RentalStatus(name="Checked Out")
    session.add(rental_status)
    session.commit()

    today = date.today()
    current_rental_date = datetime(today.year, today.month, 15, tzinfo=timezone.utc)
    previous_month = today.month - 1 or 12
    previous_year = today.year if today.month > 1 else today.year - 1
    previous_rental_date = datetime(previous_year, previous_month, 15, tzinfo=timezone.utc)

    session.add(
        Rental(
            customer_id=current_customer.customer_id,
            customer_tools_id=current_tool.id,
            rental_status_id=rental_status.rental_status_id,
            rental_date=current_rental_date,
        )
    )
    session.add(
        Rental(
            customer_id=previous_customer.customer_id,
            customer_tools_id=previous_tool.id,
            rental_status_id=rental_status.rental_status_id,
            rental_date=previous_rental_date,
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    client = app.test_client()

    response = client.get("/rentals/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Current Month" in html
    assert "Previous Month" not in html


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
