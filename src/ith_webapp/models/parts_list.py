from sqlalchemy import Column, Integer, String
from ith_webapp.database import Base

class PartsList(Base):
    __tablename__ = 'parts_list'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    # Add additional fields as needed for BOM header

class PartsSub(Base):
    __tablename__ = 'parts_sub'
    id = Column(Integer, primary_key=True)
    parts_list_id = Column(Integer, nullable=False)
    part_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    # Add additional fields as needed for BOM line items
