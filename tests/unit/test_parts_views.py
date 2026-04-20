import io

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.part import Part
from ith_webapp.models.parts_sold import PartsSold


def _create_test_app_with_part_and_sales():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(Part(part_number="P-1001", description="Test Part", active=True))
    session.commit()
    session.add(PartsSold(part_id=1, quantity=7, sold_date="2024-01-01"))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_parts_list_filters_by_item_code_or_description():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(Part(part_number="P-1001", description="Test Part", active=True))
    session.add(Part(part_number="P-2002", description="Other Part", active=True))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    client = app.test_client()

    response = client.get("/parts/?q=test")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "P-1001" in html
    assert "P-2002" not in html


def test_part_sold_history_renders_sales_for_a_part():
    app = _create_test_app_with_part_and_sales()
    client = app.test_client()

    response = client.get("/parts/1/sold-history")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "P-1001" in html
    assert "7" in html


def test_part_labels_route_renders_a_printable_label_with_barcode():
    app = _create_test_app_with_part_and_sales()
    client = app.test_client()

    response = client.get("/parts/1/labels?format=short&warehouse=Main+Warehouse")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "P-1001" in html
    assert "Test Part" in html
    assert "Main Warehouse" in html
    assert "<svg" in html


def test_part_attachments_can_be_uploaded_and_downloaded(tmp_path):
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(Part(part_number="P-3003", description="Attachment Part", active=True))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    app.config["PART_ATTACHMENT_STORAGE_ROOT"] = tmp_path
    client = app.test_client()

    response = client.post(
        "/parts/1/attachments",
        data={"file": (io.BytesIO(b"attachment contents"), "spec sheet.txt")},
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/parts/1")

    detail = client.get("/parts/1")
    assert detail.status_code == 200
    assert "spec_sheet.txt" in detail.get_data(as_text=True)

    download = client.get("/parts/1/attachments/spec_sheet.txt")

    assert download.status_code == 200
    assert download.data == b"attachment contents"
