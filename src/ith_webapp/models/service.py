from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ith_webapp.database import Base

class Service(Base):
    __tablename__ = "service"

    service_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    check_in_sub_id: Mapped[int] = mapped_column(Integer, ForeignKey("check_in_sub.id"), nullable=True)
    cardcode: Mapped[str | None] = mapped_column(String(75), nullable=True)
    order_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sale_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    order_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    technician: Mapped[str | None] = mapped_column(String(100), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    cost: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    customer = relationship("Customer", backref="services")
    check_in_sub = relationship("CheckInSub", backref="services")
