from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ith_webapp.database import Base

class CustomerApplication(Base):
    __tablename__ = "customer_application"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    customer = relationship("Customer", back_populates="applications")
    specs = relationship("CustomerApplicationSpecs", back_populates="application", cascade="all, delete-orphan")

class CustomerApplicationSpecs(Base):
    __tablename__ = "customer_application_specs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer_application.id"), nullable=False)
    key: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    application = relationship("CustomerApplication", back_populates="specs")
