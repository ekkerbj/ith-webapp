from sqlalchemy.orm import Session

from ith_webapp.models.site_gas_turbine import SiteGasTurbine
from ith_webapp.models.site_wind_gas import SiteWindGas
from ith_webapp.models.site_wind_turbine import SiteWindTurbine
from ith_webapp.models.wind_turbine_lead import WindTurbineLead
from ith_webapp.models.wind_turbine_lead_detail import WindTurbineLeadDetail


def test_wind_turbine_site_models_can_be_persisted_and_retrieved(session: Session):
    gas_site = SiteGasTurbine(
        site_name="Gas Site",
        customer_name="Acme Corp",
        location="Dallas, TX",
        notes="Gas turbine installation",
    )
    wind_site = SiteWindTurbine(
        site_name="Wind Site",
        customer_name="Acme Corp",
        location="Austin, TX",
        notes="Wind turbine installation",
    )
    wind_gas_site = SiteWindGas(
        site_name="Hybrid Site",
        wind_units=2,
        gas_units=1,
        location="Houston, TX",
        notes="Hybrid installation",
    )
    session.add_all([gas_site, wind_site, wind_gas_site])
    session.commit()

    assert session.get(SiteGasTurbine, gas_site.site_gas_turbine_id) is not None
    assert session.get(SiteWindTurbine, wind_site.site_wind_turbine_id) is not None
    assert session.get(SiteWindGas, wind_gas_site.site_wind_gas_id) is not None


def test_wind_turbine_lead_models_can_be_persisted_and_retrieved(session: Session):
    lead = WindTurbineLead(
        customer_name="Acme Corp",
        contact_name="Jordan Smith",
        phone="555-0100",
        email="jordan@example.com",
        status="New",
        notes="Interested in a wind installation",
    )
    session.add(lead)
    session.commit()

    detail = WindTurbineLeadDetail(
        wind_turbine_lead_id=lead.wind_turbine_lead_id,
        notes="Called back with pricing follow-up",
    )
    session.add(detail)
    session.commit()

    assert session.get(WindTurbineLead, lead.wind_turbine_lead_id) is not None
    assert (
        session.get(WindTurbineLeadDetail, detail.wind_turbine_lead_detail_id)
        is not None
    )
