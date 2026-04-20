from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from ith_webapp.database import Base

class CheckIn(Base):
    __tablename__ = "check_in"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    customer = relationship("Customer", backref="check_ins")
    subs = relationship("CheckInSub", back_populates="check_in", cascade="all, delete-orphan")

class CheckInSub(Base):
    __tablename__ = "check_in_sub"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    check_in_id: Mapped[int] = mapped_column(Integer, ForeignKey("check_in.id"), nullable=False)
    tool_id: Mapped[int] = mapped_column(Integer, nullable=False)
    inspected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quoted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    check_in = relationship("CheckIn", back_populates="subs")
