from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class Rental(Base):
    __tablename__ = "rental"

    rental_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.customer_id"), nullable=False
    )
    customer_tools_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer_tools.id"), nullable=False
    )
    rental_status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("rental_status.rental_status_id"), nullable=False
    )
    rental_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    return_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    customer = relationship("Customer")
    customer_tools = relationship("CustomerTools")
    rental_status = relationship("RentalStatus", back_populates="rentals")
