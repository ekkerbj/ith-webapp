from sqlalchemy.orm import Session

from ith_webapp.models import Customer
from ith_webapp.models.field_service import FieldService
from ith_webapp.models.field_service_status import FieldServiceStatus


def test_field_service_can_be_persisted_and_retrieved(session: Session):
    customer = Customer(customer_name="Field Service Customer")
    status = FieldServiceStatus(name="Open")
    session.add(customer)
    session.add(status)
    session.commit()

    field_service = FieldService(
        customer_id=customer.customer_id,
        field_service_status_id=status.field_service_status_id,
        visit_notes="On-site visit",
    )
    session.add(field_service)
    session.commit()

    result = session.get(FieldService, field_service.field_service_id)

    assert result is not None
    assert result.customer_id == customer.customer_id
    assert result.field_service_status_id == status.field_service_status_id
    assert result.visit_notes == "On-site visit"
