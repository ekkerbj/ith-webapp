from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class RentalStatus(Base):
    __tablename__ = "rental_status"

    rental_status_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    rentals = relationship("Rental", back_populates="rental_status")
