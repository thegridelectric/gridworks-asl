from typing import Literal

from sema.runtime.base import SemaType


class Gw1TankTempCalibration(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.tank.temp.calibration/000"""

    depth1_m: float = 1.0
    depth1_b: float = 0.0
    depth2_m: float = 1.0
    depth2_b: float = 0.0
    depth3_m: float = 1.0
    depth3_b: float = 0.0
    type_name: Literal["gw1.tank.temp.calibration"] = "gw1.tank.temp.calibration"
    version: Literal["000"] = "000"
