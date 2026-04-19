import pytest
from ith_webapp.models.service_measurements import ServiceMeasurements
from ith_webapp.models.service import Service
from sqlalchemy.orm import Session

def test_service_measurements_model_fields():
    sm = ServiceMeasurements(
        service_id=1,
        btc_passed=True,
        gauge_value=1.23,
        hose_pressure=2.34,
        nut_runner_torque=3.45,
        pump_output=4.56,
        torque_wrench_setting=5.67
    )
    assert sm.service_id == 1
    assert sm.btc_passed is True
    assert sm.gauge_value == 1.23
    assert sm.hose_pressure == 2.34
    assert sm.nut_runner_torque == 3.45
    assert sm.pump_output == 4.56
    assert sm.torque_wrench_setting == 5.67
