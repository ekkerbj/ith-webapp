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


def test_part_sold_history_renders_sales_for_a_part():
    app = _create_test_app_with_part_and_sales()
    client = app.test_client()

    response = client.get("/parts/1/sold-history")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "P-1001" in html
    assert "7" in html
