from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models import Customer, Service
from ith_webapp.models.warranty_claim import WarrantyClaim, WarrantyClaimQuote


def _create_test_app_with_warranty_claim():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.flush()

    service_one = Service(customer_id=customer.customer_id, cardcode="Q-100", active=True)
    service_two = Service(customer_id=customer.customer_id, cardcode="Q-200", active=True)
    session.add_all([service_one, service_two])
    session.flush()

    claim = WarrantyClaim(
        customer_id=customer.customer_id,
        claim_number="WC-1001",
        status="Open",
        notes="Initial claim",
    )
    session.add(claim)
    session.flush()
    session.add_all(
        [
            WarrantyClaimQuote(
                warranty_claim_id=claim.warranty_claim_id,
                service_id=service_one.service_id,
            ),
            WarrantyClaimQuote(
                warranty_claim_id=claim.warranty_claim_id,
                service_id=service_two.service_id,
            ),
        ]
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_warranty_claim_list_and_detail_render_linked_quote_data():
    app = _create_test_app_with_warranty_claim()
    client = app.test_client()

    list_response = client.get("/warranty-claims/")
    assert list_response.status_code == 200
    assert "WC-1001" in list_response.get_data(as_text=True)

    detail_response = client.get("/warranty-claims/1")
    assert detail_response.status_code == 200
    detail_html = detail_response.get_data(as_text=True)
    assert "WC-1001" in detail_html
    assert "Q-100" in detail_html
    assert "Q-200" in detail_html


def test_warranty_claim_create_edit_and_delete_work():
    app = _create_test_app_with_warranty_claim()
    client = app.test_client()

    create_response = client.post(
        "/warranty-claims/new",
        data={
            "customer_id": "1",
            "claim_number": "WC-2002",
            "status": "Open",
            "notes": "New claim",
            "service_ids": "1, 2",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 302

    edit_response = client.post(
        "/warranty-claims/1/edit",
        data={
            "customer_id": "1",
            "claim_number": "WC-1001A",
            "status": "Closed",
            "notes": "Updated claim",
            "service_ids": "2",
        },
        follow_redirects=False,
    )
    assert edit_response.status_code == 302

    delete_response = client.post("/warranty-claims/1/delete", follow_redirects=False)
    assert delete_response.status_code == 302
