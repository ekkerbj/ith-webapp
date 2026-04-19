from sqlalchemy import Column, Integer, ForeignKey
from ith_webapp.database import Base

class ServiceFlagAssignment(Base):
    __tablename__ = 'service_flag_assignment'
    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.service_id'), nullable=False)
    flag_id = Column(Integer, ForeignKey('service_flag.id'), nullable=False)
