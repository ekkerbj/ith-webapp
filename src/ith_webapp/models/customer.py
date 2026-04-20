from decimal import Decimal

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
    price_list_num: Mapped[int | None] = mapped_column(
        "price list num", Integer, nullable=True
    )
    salesperson: Mapped[str | None] = mapped_column(
        "salesperson", String(100), nullable=True
    )
    territory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    tax_group: Mapped[str | None] = mapped_column(
        "tax group", String(50), nullable=True
    )
    tax_exempt_number: Mapped[str | None] = mapped_column(
        "tax exempt number", String(50), nullable=True
    )
    contact_name: Mapped[str | None] = mapped_column(
        "contact name", String(100), nullable=True
    )
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    fax: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(100), nullable=True)
    plant_name: Mapped[str | None] = mapped_column(
        "plant name", String(100), nullable=True
    )
    site_name: Mapped[str | None] = mapped_column(
        "site name", String(100), nullable=True
    )
    site_address: Mapped[str | None] = mapped_column(
        "site address", String(100), nullable=True
    )
    site_city: Mapped[str | None] = mapped_column(
        "site city", String(100), nullable=True
    )
    site_state: Mapped[str | None] = mapped_column(
        "site state", String(50), nullable=True
    )
    site_zip_code: Mapped[str | None] = mapped_column(
        "site zip code", String(20), nullable=True
    )
    site_country: Mapped[str | None] = mapped_column(
        "site country", String(50), nullable=True
    )
    ship_via: Mapped[str | None] = mapped_column(
        "ship via", String(50), nullable=True
    )
    freight_terms: Mapped[str | None] = mapped_column(
        "freight terms", String(100), nullable=True
    )
    shipping_instructions: Mapped[str | None] = mapped_column(
        "shipping instructions", Text, nullable=True
    )
    billing_instructions: Mapped[str | None] = mapped_column(
        "billing instructions", Text, nullable=True
    )
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    repair_instructions: Mapped[str | None] = mapped_column(
        "repair instructions", Text, nullable=True
    )
    multiplier: Mapped[Decimal | None] = mapped_column(
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
    applications = relationship(
        "CustomerApplication",
        back_populates="customer",
        cascade="all, delete-orphan"
    )

    @property
    def sales_rep(self) -> str | None:
        return self.salesperson

    @sales_rep.setter
    def sales_rep(self, value: str | None) -> None:
        self.salesperson = value
