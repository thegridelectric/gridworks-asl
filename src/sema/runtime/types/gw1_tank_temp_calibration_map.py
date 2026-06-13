from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.types.gw1_tank_temp_calibration import Gw1TankTempCalibration


class Gw1TankTempCalibrationMap(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.tank.temp.calibration.map/000"""

    buffer: Gw1TankTempCalibration
    tank: dict[str, Gw1TankTempCalibration]
    type_name: Literal["gw1.tank.temp.calibration.map"] = (
        "gw1.tank.temp.calibration.map"
    )
    version: Literal["000"] = "000"
