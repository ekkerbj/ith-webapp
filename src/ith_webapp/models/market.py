from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base

class Market(Base):
    __tablename__ = "market"

    market_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    customers = relationship(
        "Customer",
        secondary="customer_market",
        back_populates="markets"
    )
