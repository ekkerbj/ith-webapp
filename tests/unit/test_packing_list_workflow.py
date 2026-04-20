from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.packing_list import PackingList


def test_packing_list_index_filters_by_customer_or_date():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add(PackingList(customer_name="Acme Corp", packing_date="2026-04-19"))
    session.add(PackingList(customer_name="Beta Inc", packing_date="2026-04-20"))
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    client = app.test_client()

    response = client.get("/packing-lists/?q=acme")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Acme Corp" in html
    assert "Beta Inc" not in html


def test_ready_to_produce_and_ready_to_ship_views():
    app = create_app(testing=True)
    client = app.test_client()

    response = client.get("/packing-lists/ready-to-produce")
    assert response.status_code == 501
    response = client.get("/packing-lists/ready-to-ship")
    assert response.status_code == 501
