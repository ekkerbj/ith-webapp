from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class ITHTestGauge(Base):
    __tablename__ = "ith_test_gauge"

    ith_test_gauge_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    ith_test_gauge_type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ith_test_gauge_type.ith_test_gauge_type_id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    calibration_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    certification_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    ith_test_gauge_type = relationship("ITHTestGaugeType", back_populates="gauges")
