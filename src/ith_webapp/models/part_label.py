from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class PartLabel(Base):
    __tablename__ = "part_label"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    check_in_id: Mapped[int] = mapped_column(Integer, ForeignKey("check_in.id"), nullable=False)
    check_in_sub_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("check_in_sub.id"), nullable=True
    )
    part_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("part.part_id"), nullable=True)
    part_number: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    warehouse: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    check_in = relationship("CheckIn", back_populates="part_labels")
    check_in_sub = relationship("CheckInSub")
    part = relationship("Part")
