from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class FieldServiceSub(Base):
    __tablename__ = "field_service_sub"

    field_service_sub_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    field_service_type_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("field_service_type.field_service_type_id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    field_service_type = relationship("FieldServiceType", back_populates="subs")
