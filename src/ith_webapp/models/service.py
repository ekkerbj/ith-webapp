from sqlalchemy import Integer, String, ForeignKey, DateTime, Numeric, Boolean, Text
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
    received_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    quoted_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    customer_po: Mapped[str | None] = mapped_column(String(75), nullable=True)
    invoice_number: Mapped[str | None] = mapped_column(String(75), nullable=True)
    work_order_number: Mapped[str | None] = mapped_column(String(75), nullable=True)
    assigned_technician: Mapped[str | None] = mapped_column(String(100), nullable=True)
    secondary_technician: Mapped[str | None] = mapped_column(String(100), nullable=True)
    customer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ship_via: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quote_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    customer = relationship("Customer", backref="services")
    check_in_sub = relationship("CheckInSub", backref="services")
