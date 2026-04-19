from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def _create_test_app_with_customers(*customers):
    """Create a test app with an in-memory DB seeded with given customers."""
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    for c in customers:
        session.add(c)
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_customer_list_renders_customer_names():
    app = _create_test_app_with_customers(
        Customer(customer_name="Acme Corp", card_code="C10001", active=True),
        Customer(customer_name="Beta Inc", card_code="C10002", active=True),
    )
    client = app.test_client()

    response = client.get("/customers/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Acme Corp" in html
    assert "Beta Inc" in html


def test_customer_list_renders_empty_state():
    app = _create_test_app_with_customers()
    client = app.test_client()

    response = client.get("/customers/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "No customers found" in html


def test_customer_detail_renders_customer_fields():
    app = _create_test_app_with_customers(
        Customer(
            customer_name="Acme Corp",
            card_code="C10001",
            active=True,
            website="https://acme.example.com",
            comments="Important customer",
        ),
    )
    client = app.test_client()

    response = client.get("/customers/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Acme Corp" in html
    assert "C10001" in html
    assert "https://acme.example.com" in html
    assert "Important customer" in html


def test_customer_detail_returns_404_for_missing_customer():
    app = _create_test_app_with_customers()
    client = app.test_client()

    response = client.get("/customers/9999")

    assert response.status_code == 404


def test_customer_create_form_renders():
    app = _create_test_app_with_customers()
    client = app.test_client()

    response = client.get("/customers/new")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '<form' in html
    assert 'name="customer_name"' in html


def test_customer_create_saves_and_redirects():
    app = _create_test_app_with_customers()
    client = app.test_client()

    response = client.post(
        "/customers/new",
        data={
            "customer_name": "New Corp",
            "card_code": "C30001",
            "active": "on",
            "website": "https://new.example.com",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/customers/" in response.headers["Location"]

    # Verify persisted
    list_response = client.get("/customers/")
    html = list_response.get_data(as_text=True)
    assert "New Corp" in html


def test_customer_edit_form_renders_with_existing_data():
    app = _create_test_app_with_customers(
        Customer(
            customer_name="Acme Corp",
            card_code="C10001",
            active=True,
            website="https://acme.example.com",
        ),
    )
    client = app.test_client()

    response = client.get("/customers/1/edit")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert '<form' in html
    assert 'value="Acme Corp"' in html
    assert 'value="C10001"' in html
    assert 'value="https://acme.example.com"' in html


def test_customer_edit_form_returns_404_for_missing_customer():
    app = _create_test_app_with_customers()
    client = app.test_client()

    response = client.get("/customers/9999/edit")

    assert response.status_code == 404


def test_customer_edit_updates_and_redirects():
    app = _create_test_app_with_customers(
        Customer(
            customer_name="Acme Corp",
            card_code="C10001",
            active=True,
        ),
    )
    client = app.test_client()

    response = client.post(
        "/customers/1/edit",
        data={
            "customer_name": "Acme Updated",
            "card_code": "C10001",
            "active": "on",
            "website": "https://updated.example.com",
        },
        follow_redirects=False,
    )

    assert response.status_code == 302
    assert "/customers/1" in response.headers["Location"]

    # Verify updated
    detail_response = client.get("/customers/1")
    html = detail_response.get_data(as_text=True)
    assert "Acme Updated" in html
    assert "https://updated.example.com" in html
