from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class Customer(Base):
    __tablename__ = "customer"

    customer_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_name: Mapped[str] = mapped_column(
        "customer", String(100), nullable=True
    )
    card_code: Mapped[str | None] = mapped_column(
        "cardcode", String(75), nullable=True
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    website: Mapped[str | None] = mapped_column(String(50), nullable=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    repair_instructions: Mapped[str | None] = mapped_column(
        "repair instructions", Text, nullable=True
    )
    multiplier: Mapped[float | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    lead_id: Mapped[int | None] = mapped_column(
        "lead id", Integer, nullable=True
    )
    responsibility_id: Mapped[int | None] = mapped_column(
        "responsibility id", Integer, nullable=True
    )
    calibration_interval: Mapped[int | None] = mapped_column(
        "calibration interval", Integer, nullable=True
    )

    markets = relationship(
        "Market",
        secondary="customer_market",
        back_populates="customers"
    )
    tools = relationship(
        "CustomerTools",
        back_populates="customer",
        cascade="all, delete-orphan"
    )
