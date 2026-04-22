from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.packing_list import PackingList


def _create_test_app_with_packing_list():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(PackingList())
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_cat_bar_code_label_renders_packing_list_barcode():
    app = _create_test_app_with_packing_list()
    client = app.test_client()

    response = client.get("/packing-lists/1/labels/cat")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "CAT Bar Code Label" in html
    assert "Packing List ID" in html
    assert "<svg" in html


def test_cat_bar_code_label_uses_guided_header():
    app = _create_test_app_with_packing_list()
    client = app.test_client()

    response = client.get("/packing-lists/1/labels/cat")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Label sheet" in html
    assert "Print-ready packing list label" in html


def test_zf_bar_code_label_renders_packing_list_barcode():
    app = _create_test_app_with_packing_list()
    client = app.test_client()

    response = client.get("/packing-lists/1/labels/zf")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "ZF Bar Code Label" in html
    assert "Packing List ID" in html
    assert "<svg" in html
