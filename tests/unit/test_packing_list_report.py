from ith_webapp.models import PackingList, PackingListSub


def test_packing_list_report_route_returns_pdf(app):
    factory = app.config["SESSION_FACTORY"]
    session = factory()
    try:
        packing_list = PackingList()
        session.add(packing_list)
        session.flush()

        session.add_all(
            [
                PackingListSub(
                    packing_list_id=packing_list.id,
                    harm_number="1234.56",
                    EECN="EECN-1",
                    DDTC="DDTC-1",
                    COO="USA",
                    in_bond_code="IB-1",
                ),
                PackingListSub(
                    packing_list_id=packing_list.id,
                    harm_number="7890.12",
                    EECN="EECN-2",
                    DDTC="DDTC-2",
                    COO="MEX",
                    in_bond_code="IB-2",
                ),
            ]
        )
        session.commit()

        response = app.test_client().get(f"/reports/packing-list/{packing_list.id}")

        assert response.status_code == 200
        assert response.mimetype == "application/pdf"
        assert response.data.startswith(b"%PDF")
        assert b"Packing List" in response.data
        assert b"Packing List ID" in response.data
        assert b"1234.56" in response.data
        assert b"EECN-1" in response.data
    finally:
        session.close()
