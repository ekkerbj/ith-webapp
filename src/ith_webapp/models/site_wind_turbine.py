from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ith_webapp.database import Base


class SiteWindTurbine(Base):
    __tablename__ = "sites_wind_turbine"

    site_wind_turbine_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    site_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
