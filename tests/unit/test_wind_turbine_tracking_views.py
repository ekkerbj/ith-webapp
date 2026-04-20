from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ith_webapp.app import create_app
from ith_webapp.database import Base
from ith_webapp.models.site_gas_turbine import SiteGasTurbine
from ith_webapp.models.site_wind_gas import SiteWindGas
from ith_webapp.models.site_wind_turbine import SiteWindTurbine
from ith_webapp.models.wind_turbine_lead import WindTurbineLead
from ith_webapp.models.wind_turbine_lead_detail import WindTurbineLeadDetail


def _create_test_app():
    app = create_app(testing=True)
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    session = factory()
    session.add_all(
        [
            SiteGasTurbine(
                site_name="Gas Site",
                customer_name="Acme Corp",
                location="Dallas, TX",
                notes="Gas site",
            ),
            SiteWindTurbine(
                site_name="Wind Site",
                customer_name="Acme Corp",
                location="Austin, TX",
                notes="Wind site",
            ),
            SiteWindGas(
                site_name="Hybrid Site",
                wind_units=2,
                gas_units=1,
                location="Houston, TX",
                notes="Hybrid site",
            ),
        ]
    )
    lead = WindTurbineLead(
        customer_name="Acme Corp",
        contact_name="Jordan Smith",
        phone="555-0100",
        email="jordan@example.com",
        status="New",
        notes="Interested in wind turbines",
    )
    session.add(lead)
    session.commit()
    session.add(
        WindTurbineLeadDetail(
            wind_turbine_lead_id=lead.wind_turbine_lead_id,
            notes="Called back for follow-up",
        )
    )
    session.commit()
    session.close()

    app.config["SESSION_FACTORY"] = factory
    return app


def test_site_gas_turbine_crud_views_work():
    app = _create_test_app()
    client = app.test_client()

    response = client.get("/sites-gas-turbines/")
    assert response.status_code == 200
    assert "Gas Site" in response.get_data(as_text=True)

    response = client.get("/sites-gas-turbines/1")
    assert response.status_code == 200
    assert "Dallas, TX" in response.get_data(as_text=True)

    response = client.post(
        "/sites-gas-turbines/new",
        data={
            "site_name": "New Gas Site",
            "customer_name": "New Customer",
            "location": "Lubbock, TX",
            "notes": "New",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/sites-gas-turbines/" in response.headers["Location"]

    response = client.post(
        "/sites-gas-turbines/1/edit",
        data={
            "site_name": "Updated Gas Site",
            "customer_name": "Acme Corp",
            "location": "El Paso, TX",
            "notes": "Updated",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/sites-gas-turbines/1" in response.headers["Location"]

    response = client.post("/sites-gas-turbines/1/delete", follow_redirects=False)
    assert response.status_code == 302


def test_wind_turbine_lead_crud_views_work():
    app = _create_test_app()
    client = app.test_client()

    response = client.get("/wind-turbine-leads/")
    assert response.status_code == 200
    assert "Acme Corp" in response.get_data(as_text=True)

    response = client.get("/wind-turbine-leads/1")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Jordan Smith" in html
    assert "Called back for follow-up" in html

    response = client.post(
        "/wind-turbine-leads/new",
        data={
            "customer_name": "Beta Corp",
            "contact_name": "Taylor Lee",
            "phone": "555-0200",
            "email": "taylor@example.com",
            "status": "New",
            "notes": "New lead",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/wind-turbine-leads/" in response.headers["Location"]

    response = client.post(
        "/wind-turbine-leads/1/edit",
        data={
            "customer_name": "Acme Corp",
            "contact_name": "Jordan Smith",
            "phone": "555-0101",
            "email": "jordan@example.com",
            "status": "Working",
            "notes": "Updated lead",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert "/wind-turbine-leads/1" in response.headers["Location"]

    response = client.post("/wind-turbine-leads/1/delete", follow_redirects=False)
    assert response.status_code == 302
