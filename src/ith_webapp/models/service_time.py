from sqlalchemy import Integer, String, ForeignKey, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from ith_webapp.database import Base

class ServiceTime(Base):
    __tablename__ = "service_time"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("service.service_id"), nullable=False)
    technician: Mapped[str] = mapped_column(String(100), nullable=False)
    hours: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    date: Mapped[str] = mapped_column(String(10), nullable=False)  # ISO date string for simplicity
    labor_rate: Mapped[float] = mapped_column(Numeric(7, 2), nullable=False)
