from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from ith_webapp.database import Base

class CustomerMarket(Base):
    __tablename__ = "customer_market"

    customer_market_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customer.customer_id"), nullable=False)
    market_id: Mapped[int] = mapped_column(ForeignKey("market.market_id"), nullable=False)
