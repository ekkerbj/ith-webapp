from ith_webapp.models.audit_trail import AuditTrail  # noqa: F401
from ith_webapp.models.customer import Customer
from ith_webapp.app import create_app
from ith_webapp.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def test_record_audit_change_logs_field_changes(session):
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.commit()

    from ith_webapp.services.audit_trail import get_audit_history, record_audit_change

    record_audit_change(
        session,
        table_name="customer",
        record_id=customer.customer_id,
        action="edit",
        changes={"customer_name": ("Acme Corp", "Acme Updated")},
    )
    session.commit()

    history = get_audit_history(session, table_name="customer", record_id=customer.customer_id)

    assert len(history) == 1
    entry = history[0]
    assert entry.field_name == "customer_name"
    assert entry.old_value == "Acme Corp"
    assert entry.new_value == "Acme Updated"
    assert entry.action == "edit"


def test_customer_edit_records_and_renders_audit_history():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    session.add(customer)
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
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

    history_response = client.get("/audit-trail/customer/1")
    html = history_response.get_data(as_text=True)

    assert "customer_name" in html
    assert "Acme Corp" in html
    assert "Acme Updated" in html
