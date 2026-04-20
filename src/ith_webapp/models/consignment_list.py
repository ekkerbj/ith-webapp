from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class ConsignmentList(Base):
    __tablename__ = "consignment_list"

    consignment_list_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.customer_id"), nullable=False
    )
    part_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("part.part_id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    customer = relationship("Customer")
    part = relationship("Part")
