from sqlalchemy import Column, Integer, String
from ith_webapp.database import Base

class Unit(Base):
    __tablename__ = 'unit'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
