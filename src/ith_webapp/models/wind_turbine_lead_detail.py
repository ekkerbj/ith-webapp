from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class WindTurbineLeadDetail(Base):
    __tablename__ = "wind_turbine_leads_details"

    wind_turbine_lead_detail_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    wind_turbine_lead_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("wind_turbine_leads.wind_turbine_lead_id"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    wind_turbine_lead = relationship("WindTurbineLead", back_populates="details")
