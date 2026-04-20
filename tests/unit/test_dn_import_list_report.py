from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.part import Part
from ith_webapp.models.parts_sold import PartsSold


def _create_app_with_dn_import_data():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    part = Part(part_number="DN-100", description="Imported part", active=True)
    session.add(part)
    session.commit()
    session.add(PartsSold(part_id=part.part_id, quantity=12, sold_date="2026-04-19"))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_dn_import_list_report_shows_parts_sold_rows():
    app = _create_app_with_dn_import_data()

    response = app.test_client().get("/reports/dn-import-list")

    assert response.status_code == 200
    assert response.mimetype == "text/html"
    body = response.get_data(as_text=True)
    assert "DN Import List" in body
    assert "DN-100" in body
    assert "Imported part" in body
    assert "2026-04-19" in body
