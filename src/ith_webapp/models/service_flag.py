from sqlalchemy import Column, Integer, String, Text
from ith_webapp.database import Base

class ServiceFlag(Base):
    __tablename__ = 'service_flag'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
