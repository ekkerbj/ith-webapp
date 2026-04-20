from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ith_webapp.database import Base


class FieldServiceType(Base):
    __tablename__ = "field_service_type"

    field_service_type_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    subs = relationship(
        "FieldServiceSub",
        back_populates="field_service_type",
        cascade="all, delete-orphan",
    )
