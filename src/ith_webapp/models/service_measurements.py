from sqlalchemy import Integer, String, ForeignKey, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ith_webapp.database import Base

class ServiceMeasurements(Base):
    __tablename__ = "service_measurements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("service.service_id"), nullable=False)
    # Example fields, actual implementation may require ~100 fields as per spec
    btc_passed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    gauge_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    hose_pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    nut_runner_torque: Mapped[float | None] = mapped_column(Float, nullable=True)
    pump_output: Mapped[float | None] = mapped_column(Float, nullable=True)
    torque_wrench_setting: Mapped[float | None] = mapped_column(Float, nullable=True)

    service = relationship("Service", backref="measurements")

    def item_sum(self, session):
        from ith_webapp.models.service_sub import ServiceSub
        result = session.query(ServiceSub).filter_by(service_id=self.service_id, item_type='I').all()
        return sum(sub.cost for sub in result)

    def labor_sum(self, session):
        from ith_webapp.models.service_sub import ServiceSub
        result = session.query(ServiceSub).filter_by(service_id=self.service_id, item_type='L').all()
        return sum(sub.cost for sub in result)
