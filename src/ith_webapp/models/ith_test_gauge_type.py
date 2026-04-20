from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class ITHTestGaugeType(Base):
    __tablename__ = "ith_test_gauge_type"

    ith_test_gauge_type_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    gauges = relationship("ITHTestGauge", back_populates="ith_test_gauge_type")
