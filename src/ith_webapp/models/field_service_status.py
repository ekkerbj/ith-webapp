from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ith_webapp.database import Base


class FieldServiceStatus(Base):
    __tablename__ = "field_service_status"

    field_service_status_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
