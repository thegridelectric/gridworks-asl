from pydantic import ValidationError

from sema.runtime.types.gw1_tank_temp_calibration import Gw1TankTempCalibration
from sema.runtime.types.gw1_tank_temp_calibration_map import Gw1TankTempCalibrationMap


def test_calibration_map_requires_contiguous_tanks() -> None:
    cal = Gw1TankTempCalibration()
    try:
        Gw1TankTempCalibrationMap(
            buffer=cal,
            tank={"1": cal, "3": cal},
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
