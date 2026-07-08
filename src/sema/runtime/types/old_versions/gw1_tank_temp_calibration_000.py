from typing import Literal
from pydantic import StrictFloat
from sema.runtime.base import SemaType
from sema.runtime.types.gw1_tank_temp_calibration import Gw1TankTempCalibration


class Gw1TankTempCalibration000(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.tank.temp.calibration/000"""

    depth1_m: StrictFloat = 1.0
    depth1_b: StrictFloat = 0.0
    depth2_m: StrictFloat = 1.0
    depth2_b: StrictFloat = 0.0
    depth3_m: StrictFloat = 1.0
    depth3_b: StrictFloat = 0.0
    type_name: Literal["gw1.tank.temp.calibration"] = "gw1.tank.temp.calibration"
    version: Literal["000"] = "000"

    def upgrade(self) -> Gw1TankTempCalibration:
        """
        - Depth{1,2,3}B: number -> integer (offset in the OutputUnit/FahrenheitX100 scaling
          domain, mirroring linear.one.dimensional.calibration/001)
        """
        data = self.model_dump()
        data["depth1_b"] = round(self.depth1_b * 100)
        data["depth2_b"] = round(self.depth2_b * 100)
        data["depth3_b"] = round(self.depth3_b * 100)
        data["version"] = "001"
        return Gw1TankTempCalibration.model_validate(data)
