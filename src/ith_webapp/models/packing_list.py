from sqlalchemy import Column, Integer, String
from ith_webapp.database import Base

class PackingList(Base):
    __tablename__ = 'packing_list'

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(100), nullable=True)
    packing_date = Column(String(10), nullable=True)
