from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ith_webapp.database import Base


class SiteWindGas(Base):
    __tablename__ = "sites_wind_gas"

    site_wind_gas_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    site_name: Mapped[str] = mapped_column(String(100), nullable=False)
    wind_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gas_units: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[str | None] = mapped_column(String(150), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
