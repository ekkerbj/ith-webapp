import csv
import io

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.customer import Customer
from ith_webapp.models.field_service import FieldService
from ith_webapp.models.field_service_status import FieldServiceStatus
from ith_webapp.models.part import Part
from ith_webapp.models.packing_list import PackingList


def _csv_rows(response):
    return list(csv.reader(io.StringIO(response.get_data(as_text=True))))


def _make_app():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    app.config["SESSION_FACTORY"] = sessionmaker(bind=engine)
    return app, sessionmaker(bind=engine)


def _seed_customer(factory):
    session = factory()
    session.add(Customer(customer_name="Acme Corp", card_code="C10001", active=True))
    session.commit()
    session.close()


def _seed_part(factory):
    session = factory()
    session.add(Part(part_number="P-1001", description="Test Part", active=True))
    session.commit()
    session.close()


def _seed_packing_list(factory):
    session = factory()
    session.add(PackingList(customer_name="Acme Corp", packing_date="2026-04-19"))
    session.commit()
    session.close()


def _seed_field_service(factory):
    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    status = FieldServiceStatus(name="Open")
    session.add_all([customer, status])
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


@pytest.mark.parametrize(
    "path,seed,expected_headers,expected_row",
    [
        ("/customers/", _seed_customer, ["Name", "Card Code", "Active"], ["Acme Corp", "C10001", "Yes"]),
        ("/parts/", _seed_part, ["Item Code", "Description", "Active"], ["P-1001", "Test Part", "Yes"]),
        ("/packing-lists/", _seed_packing_list, ["Customer", "Packing Date", "ID"], ["Acme Corp", "2026-04-19", "1"]),
        (
            "/field-services/",
            _seed_field_service,
            ["Customer", "Status", "Notes"],
            ["Acme Corp", "Open", "On-site visit"],
        ),
    ],
)
def test_main_list_views_export_csv(path, seed, expected_headers, expected_row):
    app, factory = _make_app()
    seed(factory)
    client = app.test_client()

    response = client.get(f"{path}?format=csv")

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert "attachment" in response.headers["Content-Disposition"]
    rows = _csv_rows(response)
    assert rows[0] == expected_headers
    assert rows[1] == expected_row


@pytest.mark.parametrize(
    "path,seed,expected_row",
    [
        ("/customers/", _seed_customer, ["Acme Corp", "C10001", "Yes"]),
        ("/parts/", _seed_part, ["P-1001", "Test Part", "Yes"]),
        ("/packing-lists/", _seed_packing_list, ["Acme Corp", "2026-04-19", "1"]),
        (
            "/field-services/",
            _seed_field_service,
            ["Acme Corp", "Open", "On-site visit"],
        ),
    ],
)
def test_main_list_views_export_excel(path, seed, expected_row):
    app, factory = _make_app()
    seed(factory)
    client = app.test_client()

    response = client.get(f"{path}?format=excel")

    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/vnd.ms-excel")
    assert "attachment" in response.headers["Content-Disposition"]
    assert "\t".join(expected_row) in response.get_data(as_text=True)
