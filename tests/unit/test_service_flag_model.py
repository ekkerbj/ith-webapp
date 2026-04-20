import pytest
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from ith_webapp.database import Base

# ServiceFlag and ServiceFlagAssignment do not exist yet, this test should fail (Red phase)
def test_create_service_flag():
    from ith_webapp.models.service_flag import ServiceFlag
    flag = ServiceFlag(
        name="Test Flag",
        description="A test flag for services."
    )
    assert flag.name == "Test Flag"
    assert flag.description == "A test flag for services."

def test_create_service_flag_assignment():
    from ith_webapp.models.service_flag_assignment import ServiceFlagAssignment
    assignment = ServiceFlagAssignment(
        service_id=1,
        flag_id=1
    )
    assert assignment.service_id == 1
    assert assignment.flag_id == 1
