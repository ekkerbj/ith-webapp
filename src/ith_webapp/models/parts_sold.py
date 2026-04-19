from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ith_webapp.database import Base


class PartsSold(Base):
    __tablename__ = "parts_sold"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    part_id: Mapped[int] = mapped_column(Integer, ForeignKey("part.part_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    sold_date: Mapped[str] = mapped_column(String(10), nullable=False)
