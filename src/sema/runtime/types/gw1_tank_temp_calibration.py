from typing import Literal
from pydantic import StrictFloat, StrictInt
from sema.runtime.base import SemaType


class Gw1TankTempCalibration(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.tank.temp.calibration/001"""

    depth1_m: StrictFloat = 1.0
    depth1_b: StrictInt = 0
    depth2_m: StrictFloat = 1.0
    depth2_b: StrictInt = 0
    depth3_m: StrictFloat = 1.0
    depth3_b: StrictInt = 0
    type_name: Literal["gw1.tank.temp.calibration"] = "gw1.tank.temp.calibration"
    version: Literal["001"] = "001"
