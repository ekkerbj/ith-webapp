from sqlalchemy.orm import Session

from ith_webapp.models import PackingList, PackingListSub
from ith_webapp.reports import build_commercial_invoice_and_sli_pdf


def test_build_commercial_invoice_and_sli_pdf_includes_shipping_sections(
    session: Session,
):
    packing_list = PackingList()
    session.add(packing_list)
    session.flush()

    session.add(
        PackingListSub(
            packing_list_id=packing_list.id,
            harm_number="1234.56",
            EECN="EECN-1",
            DDTC="DDTC-1",
            COO="USA",
            in_bond_code="IB-1",
        )
    )
    session.commit()

    pdf_bytes = build_commercial_invoice_and_sli_pdf(session, packing_list.id)

    assert pdf_bytes.startswith(b"%PDF")
    assert b"Commercial Invoice" in pdf_bytes
    assert b"Shipper's Letter of Instruction" in pdf_bytes
    assert b"Packing List ID" in pdf_bytes
    assert b"1234.56" in pdf_bytes


def test_commercial_invoice_and_sli_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        packing_list = PackingList()
        session.add(packing_list)
        session.flush()

        session.add(
            PackingListSub(
                packing_list_id=packing_list.id,
                harm_number="1234.56",
                EECN="EECN-1",
                DDTC="DDTC-1",
                COO="USA",
                in_bond_code="IB-1",
            )
        )
        session.commit()

        response = app.test_client().get(
            f"/reports/commercial-invoice-and-sli/{packing_list.id}"
        )

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
    finally:
        session.close()
