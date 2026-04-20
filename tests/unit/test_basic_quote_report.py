from sqlalchemy.orm import Session

from ith_webapp.models import Part, PartsList, PartsSub
from ith_webapp.reports import build_basic_quote_pdf


def test_build_basic_quote_pdf_includes_bom_terms_and_variants(session: Session):
    part = Part(part_number="P-100", description="Main assembly", active=True)
    parts_list = PartsList(name="Standard Quote BOM")
    session.add_all([part, parts_list])
    session.flush()

    session.add(PartsSub(parts_list_id=parts_list.id, part_id=part.part_id, quantity=2))
    session.commit()

    pdf_bytes = build_basic_quote_pdf(session, parts_list.id, region="BR")

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Basic Quote" in pdf_bytes
    assert b"Brazil" in pdf_bytes
    assert b"-BR" in pdf_bytes
    assert b"Bill of Materials" in pdf_bytes
    assert b"Terms and Conditions" in pdf_bytes
    assert b"Why ITH" in pdf_bytes
    assert b"Credit References" in pdf_bytes
    assert b"P-100" in pdf_bytes


def test_basic_quote_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        part = Part(part_number="P-200", description="Support bracket", active=True)
        parts_list = PartsList(name="Route Quote BOM")
        session.add_all([part, parts_list])
        session.flush()

        session.add(
            PartsSub(parts_list_id=parts_list.id, part_id=part.part_id, quantity=1)
        )
        session.commit()

        response = app.test_client().get(f"/reports/basic-quote/{parts_list.id}?region=MX")

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
