from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.ith_test_gauge import ITHTestGauge
from ith_webapp.models.ith_test_gauge_type import ITHTestGaugeType


def _create_test_app_with_gauges():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    gauge_type = ITHTestGaugeType(name="Micrometer")
    session.add(gauge_type)
    session.commit()
    session.add(
        ITHTestGauge(
            ith_test_gauge_type_id=gauge_type.ith_test_gauge_type_id,
            name="Gauge A",
            serial_number="TG-001",
            calibration_due_date=date(2026, 12, 31),
            certification_due_date=date(2026, 11, 30),
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_ith_test_gauge_list_renders_gauge_data():
    app = _create_test_app_with_gauges()
    client = app.test_client()

    response = client.get("/ith-test-gauges/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Gauge A" in html
    assert "Micrometer" in html


def test_ith_test_gauge_detail_renders_gauge_data():
    app = _create_test_app_with_gauges()
    client = app.test_client()

    response = client.get("/ith-test-gauges/1")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "TG-001" in html
    assert "2026-12-31" in html
    assert "2026-11-30" in html


def test_ith_test_gauge_create_and_edit_routes_work():
    app = _create_test_app_with_gauges()
    client = app.test_client()

    create_response = client.post(
        "/ith-test-gauges/new",
        data={
            "ith_test_gauge_type_id": "1",
            "name": "Gauge B",
            "serial_number": "TG-002",
            "calibration_due_date": "2026-10-31",
            "certification_due_date": "2026-09-30",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 302

    edit_response = client.post(
        "/ith-test-gauges/1/edit",
        data={
            "ith_test_gauge_type_id": "1",
            "name": "Gauge A Updated",
            "serial_number": "TG-001",
            "calibration_due_date": "2026-12-31",
            "certification_due_date": "2026-11-30",
        },
        follow_redirects=False,
    )
    assert edit_response.status_code == 302


def test_ith_test_gauge_delete_route_works():
    app = _create_test_app_with_gauges()
    client = app.test_client()

    response = client.post("/ith-test-gauges/1/delete", follow_redirects=False)

    assert response.status_code == 302


def test_ith_test_gauge_calibration_label_route_renders_a_printable_label():
    app = _create_test_app_with_gauges()
    client = app.test_client()

    response = client.get("/ith-test-gauges/1/labels/calibration")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Gauge Calibration Label" in html
    assert "Gauge A" in html
    assert "TG-001" in html
    assert "<svg" in html


def test_ith_test_gauge_certification_label_route_renders_a_printable_label():
    app = _create_test_app_with_gauges()
    client = app.test_client()

    response = client.get("/ith-test-gauges/1/labels/certification")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Force Certification Label" in html
    assert "Gauge A" in html
    assert "TG-001" in html
    assert "<svg" in html
