from sqlalchemy import Column, Integer, String, ForeignKey
from ith_webapp.database import Base

class PackingListSub(Base):
    __tablename__ = 'packing_list_sub'

    id = Column(Integer, primary_key=True)
    packing_list_id = Column(Integer, ForeignKey('packing_list.id'), nullable=False)
    harm_number = Column(String(32), nullable=True)
    EECN = Column(String(32), nullable=True)
    DDTC = Column(String(32), nullable=True)
    COO = Column(String(32), nullable=True)
    in_bond_code = Column(String(32), nullable=True)
    # Add other fields as needed for line items
