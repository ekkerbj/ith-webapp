from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ith_webapp.database import Base

class CustomerTools(Base):
    __tablename__ = 'customer_tools'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customer.customer_id'), nullable=False)
    serial_number = Column(String, nullable=False)
    fab_number = Column(String)
    model_info = Column(String)
    unit_id = Column(Integer, ForeignKey('unit.id'))
    customer = relationship('Customer', back_populates='tools')
    subs = relationship('CustomerToolsSub', back_populates='tool', cascade='all, delete-orphan')

class CustomerToolsSub(Base):
    __tablename__ = 'customer_tools_sub'
    id = Column(Integer, primary_key=True)
    tool_id = Column(Integer, ForeignKey('customer_tools.id'), nullable=False)
    sub_type = Column(String)
    value = Column(String)
    tool = relationship('CustomerTools', back_populates='subs')
