from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.part import Part
from ith_webapp.models.customer import Customer
from ith_webapp.models.consignment_list import ConsignmentList
from ith_webapp.models.parts_list import PartsList, PartsSub
from ith_webapp.models.parts_sold import PartsSold
from ith_webapp.reports import (
    build_customer_parts_list_pdf,
    build_parts_sold_history_pdf,
    build_parts_list_pdf,
)


def _create_app_with_parts_history_data():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    part = Part(part_number="P-4001", description="Sold item", active=True)
    session.add(part)
    session.commit()
    session.add_all(
        [
            PartsSold(part_id=part.part_id, quantity=3, sold_date="2024-02-01"),
            PartsSold(part_id=part.part_id, quantity=5, sold_date="2024-03-15"),
        ]
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def _create_app_with_parts_list_data():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    part = Part(part_number="P-5001", description="Assembly part", active=True)
    parts_list = PartsList(name="Assembly BOM")
    session.add_all([part, parts_list])
    session.commit()
    session.add(PartsSub(parts_list_id=parts_list.id, part_id=part.part_id, quantity=4))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def _create_app_with_customer_parts_data():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    part = Part(part_number="P-6001", description="Customer part", active=True)
    session.add_all([customer, part])
    session.commit()
    session.add(ConsignmentList(customer_id=customer.customer_id, part_id=part.part_id, quantity=9))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_build_parts_sold_history_pdf_includes_sales_rows(session):
    part = Part(part_number="P-4001", description="Sold item", active=True)
    session.add(part)
    session.commit()
    session.add_all(
        [
            PartsSold(part_id=part.part_id, quantity=3, sold_date="2024-02-01"),
            PartsSold(part_id=part.part_id, quantity=5, sold_date="2024-03-15"),
        ]
    )
    session.commit()

    pdf_bytes = build_parts_sold_history_pdf(session, part.part_id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Parts Sold History" in pdf_bytes
    assert b"P-4001" in pdf_bytes
    assert b"2024-03-15" in pdf_bytes


def test_parts_sold_history_report_route_returns_html():
    app = _create_app_with_parts_history_data()
    client = app.test_client()

    response = client.get("/reports/parts-sold/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Parts Sold History" in html
    assert "2024-03-15" in html


def test_build_parts_list_pdf_includes_bom_rows(session):
    part = Part(part_number="P-5001", description="Assembly part", active=True)
    parts_list = PartsList(name="Assembly BOM")
    session.add_all([part, parts_list])
    session.commit()
    session.add(PartsSub(parts_list_id=parts_list.id, part_id=part.part_id, quantity=4))
    session.commit()

    pdf_bytes = build_parts_list_pdf(session, parts_list.id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Assembly BOM" in pdf_bytes
    assert b"P-5001" in pdf_bytes
    assert b"Qty 4" in pdf_bytes


def test_parts_list_report_route_returns_html():
    app = _create_app_with_parts_list_data()
    client = app.test_client()

    response = client.get("/reports/parts-list/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Assembly Parts List" in html
    assert "P-5001" in html


def test_build_customer_parts_list_pdf_includes_customer_rows(session):
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    part = Part(part_number="P-6001", description="Customer part", active=True)
    session.add_all([customer, part])
    session.commit()
    session.add(ConsignmentList(customer_id=customer.customer_id, part_id=part.part_id, quantity=9))
    session.commit()

    pdf_bytes = build_customer_parts_list_pdf(session, customer.customer_id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Acme Corp" in pdf_bytes
    assert b"P-6001" in pdf_bytes
    assert b"Qty 9" in pdf_bytes


def test_customer_parts_list_report_route_returns_html():
    app = _create_app_with_customer_parts_data()
    client = app.test_client()

    response = client.get("/reports/customer-parts-list/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Customer-Specific Parts List" in html
    assert "P-6001" in html
