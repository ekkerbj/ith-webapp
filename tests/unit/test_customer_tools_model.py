import pytest
from ith_webapp.models.customer_tools import CustomerTools, CustomerToolsSub
from ith_webapp.models.customer import Customer
from ith_webapp.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    sess = Session()
    yield sess
    sess.close()

def test_create_customer_tools(session):
    customer = Customer(customer_name="Test Customer")
    session.add(customer)
    session.commit()
    tool = CustomerTools(customer_id=customer.customer_id, serial_number="SN123", fab_number="FAB1", model_info="ModelX")
    session.add(tool)
    session.commit()
    assert tool.id is not None
    assert tool.customer_id == customer.customer_id

def test_add_sub_to_tool(session):
    customer = Customer(customer_name="Test Customer")
    session.add(customer)
    session.commit()
    tool = CustomerTools(customer_id=customer.customer_id, serial_number="SN123")
    session.add(tool)
    session.commit()
    sub = CustomerToolsSub(tool_id=tool.id, sub_type="Calibration", value="2026-04-19")
    session.add(sub)
    session.commit()
    assert sub.id is not None
    assert sub.tool_id == tool.id
