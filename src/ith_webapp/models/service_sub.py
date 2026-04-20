from sqlalchemy import Column, Integer, Float, String, ForeignKey
from ith_webapp.database import Base

class ServiceSub(Base):
    __tablename__ = 'service_sub'

    id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('service.service_id'), nullable=False)
    item_type = Column(String(1), nullable=False)  # 'I' for item, 'L' for labor
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    cost = Column(Float, nullable=False)
