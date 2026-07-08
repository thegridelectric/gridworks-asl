from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.types.gw1_tank_temp_calibration_map import Gw1TankTempCalibrationMap
from sema.runtime.types.old_versions.gw1_tank_temp_calibration_000 import (
    Gw1TankTempCalibration000,
)


class Gw1TankTempCalibrationMap000(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.tank.temp.calibration.map/000"""

    buffer: Gw1TankTempCalibration000
    tank: dict[str, Gw1TankTempCalibration000]
    type_name: Literal["gw1.tank.temp.calibration.map"] = (
        "gw1.tank.temp.calibration.map"
    )
    version: Literal["000"] = "000"

    def upgrade(self) -> Gw1TankTempCalibrationMap:
        """
        - Buffer/Tank now reference gw1.tank.temp.calibration:001 (integer B)
        """
        data = self.model_dump()
        data["buffer"] = self.buffer.upgrade().model_dump()
        data["tank"] = {k: v.upgrade().model_dump() for k, v in self.tank.items()}
        data["version"] = "001"
        return Gw1TankTempCalibrationMap.model_validate(data)
