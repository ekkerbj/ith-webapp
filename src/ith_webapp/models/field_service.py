from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class FieldService(Base):
    __tablename__ = "field_service"

    field_service_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("customer.customer_id"), nullable=False
    )
    field_service_status_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("field_service_status.field_service_status_id"),
        nullable=False,
    )
    visit_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    visit_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer = relationship("Customer", backref="field_services")
    field_service_status = relationship("FieldServiceStatus")
