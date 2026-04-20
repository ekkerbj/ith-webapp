from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.consignment_list import ConsignmentList
from ith_webapp.models.customer import Customer
from ith_webapp.models.part import Part
from ith_webapp.models.parts_list import PartsList, PartsSub
from ith_webapp.reports import build_parts_catalog_pdf


def _create_test_app_with_parts_catalog_data():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    part = Part(part_number="P-3001", description="Catalog item", active=True)
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    parts_list = PartsList(name="Catalog BOM")
    session.add_all([part, customer, parts_list])
    session.flush()
    session.add(PartsSub(parts_list_id=parts_list.id, part_id=part.part_id, quantity=4))
    session.add(
        ConsignmentList(customer_id=customer.customer_id, part_id=part.part_id, quantity=12)
    )
    session.commit()
    parts_list_name = parts_list.name
    part_id = part.part_id
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app, parts_list_name, part_id


def test_build_parts_catalog_pdf_includes_bom_and_cross_references(session):
    part = Part(part_number="P-3001", description="Catalog item", active=True)
    customer = Customer(customer_name="Acme Corp", card_code="C10001", active=True)
    parts_list = PartsList(name="Catalog BOM")
    session.add_all([part, customer, parts_list])
    session.flush()
    session.add(PartsSub(parts_list_id=parts_list.id, part_id=part.part_id, quantity=4))
    session.add(
        ConsignmentList(customer_id=customer.customer_id, part_id=part.part_id, quantity=12)
    )
    session.commit()

    pdf_bytes = build_parts_catalog_pdf(session, part.part_id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Parts Catalog" in pdf_bytes
    assert b"P-3001" in pdf_bytes
    assert b"Bill of Materials" in pdf_bytes
    assert b"Customer Cross-References" in pdf_bytes


def test_parts_catalog_report_route_returns_html():
    app, parts_list_name, part_id = _create_test_app_with_parts_catalog_data()
    client = app.test_client()

    response = client.get(f"/reports/parts/{part_id}")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Parts Catalog" in html
    assert parts_list_name in html
    assert "Customer Cross-References" in html
