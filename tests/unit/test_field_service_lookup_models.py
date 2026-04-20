from sqlalchemy.orm import Session

from ith_webapp.models.field_service_sub import FieldServiceSub
from ith_webapp.models.field_service_type import FieldServiceType


def test_field_service_type_and_sub_can_be_persisted_and_retrieved(session: Session):
    service_type = FieldServiceType(name="Repair")
    session.add(service_type)
    session.commit()

    service_sub = FieldServiceSub(
        field_service_type_id=service_type.field_service_type_id,
        name="Hydraulics",
    )
    session.add(service_sub)
    session.commit()

    result = session.get(FieldServiceSub, service_sub.field_service_sub_id)

    assert result is not None
    assert result.field_service_type_id == service_type.field_service_type_id
    assert result.name == "Hydraulics"
