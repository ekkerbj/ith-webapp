from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class WindTurbineLead(Base):
    __tablename__ = "wind_turbine_leads"

    wind_turbine_lead_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    contact_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    details = relationship(
        "WindTurbineLeadDetail",
        back_populates="wind_turbine_lead",
        cascade="all, delete-orphan",
    )
