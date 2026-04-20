from datetime import datetime, timezone

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


def test_audit_trail_report_filters_by_entity_field_and_date_range(app, client):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        session.add_all(
            [
                AuditTrail(
                    table_name="customer",
                    record_id=1,
                    field_name="website",
                    old_value="https://old.example.com",
                    new_value="https://new.example.com",
                    action="edit",
                    changed_by="tester@example.com",
                    changed_at=datetime(2026, 4, 20, tzinfo=timezone.utc),
                ),
                AuditTrail(
                    table_name="customer",
                    record_id=2,
                    field_name="card_code",
                    old_value="C0001",
                    new_value="C0002",
                    action="edit",
                    changed_by="other@example.com",
                    changed_at=datetime(2026, 4, 20, tzinfo=timezone.utc),
                ),
            ]
        )
        session.commit()

        response = client.get(
            "/reports/audit-trail?entity=customer&field=website&user=tester@example.com&start_date=2026-04-20&end_date=2026-04-20"
        )

        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "website" in html
        assert "card_code" not in html
    finally:
        session.close()
