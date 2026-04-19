import pytest
from sqlalchemy.orm import Session
from ith_webapp.models import Customer, CustomerApplication, CustomerApplicationSpecs

def test_customer_application_and_specs_persistence(session: Session):
    customer = Customer(customer_name="Test Customer")
    app = CustomerApplication(name="Calibration", description="Calibration App")
    spec = CustomerApplicationSpecs(key="frequency", value="monthly")
    app.specs.append(spec)
    customer.applications.append(app)
    session.add(customer)
    session.commit()
    session.refresh(customer)
    assert customer.applications[0].name == "Calibration"
    assert customer.applications[0].specs[0].key == "frequency"
    assert customer.applications[0].specs[0].value == "monthly"
