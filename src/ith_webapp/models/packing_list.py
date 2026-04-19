from sqlalchemy import Column, Integer, String
from ith_webapp.database import Base

class PackingList(Base):
    __tablename__ = 'packing_list'

    id = Column(Integer, primary_key=True)
    # Add additional fields as needed for header info
