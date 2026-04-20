from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class WarrantyClaim(Base):
    __tablename__ = "warranty_claim"

    warranty_claim_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.customer_id"), nullable=False
    )
    claim_number: Mapped[str | None] = mapped_column(String(75), nullable=True)
    status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer = relationship("Customer", backref="warranty_claims")
    quotes = relationship(
        "WarrantyClaimQuote",
        back_populates="warranty_claim",
        cascade="all, delete-orphan",
        order_by="WarrantyClaimQuote.id",
    )


class WarrantyClaimQuote(Base):
    __tablename__ = "warranty_claim_quote"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    warranty_claim_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("warranty_claim.warranty_claim_id"), nullable=False
    )
    service_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("service.service_id"), nullable=False
    )

    warranty_claim = relationship("WarrantyClaim", back_populates="quotes")
    service = relationship("Service")
