from datetime import date

from ith_webapp.models.ith_test_gauge import ITHTestGauge
from ith_webapp.models.ith_test_gauge_type import ITHTestGaugeType


def test_ith_test_gauge_type_and_gauge_can_be_persisted_and_retrieved(session):
    gauge_type = ITHTestGaugeType(name="Micrometer")
    session.add(gauge_type)
    session.commit()

    gauge = ITHTestGauge(
        ith_test_gauge_type_id=gauge_type.ith_test_gauge_type_id,
        name="Gauge A",
        serial_number="TG-001",
        calibration_due_date=date(2026, 12, 31),
        certification_due_date=date(2026, 11, 30),
    )
    session.add(gauge)
    session.commit()

    result = session.get(ITHTestGauge, gauge.ith_test_gauge_id)

    assert result is not None
    assert result.ith_test_gauge_type_id == gauge_type.ith_test_gauge_type_id
    assert result.name == "Gauge A"
