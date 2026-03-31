from typing import Literal

from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.types.gw1_tank_temp_calibration import Gw1TankTempCalibration


class Gw1TankTempCalibrationMap(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.tank.temp.calibration.map/000"""

    buffer: Gw1TankTempCalibration
    tank: dict[str, Gw1TankTempCalibration]
    type_name: Literal["gw1.tank.temp.calibration.map"] = "gw1.tank.temp.calibration.map"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1TankTempCalibrationMap":
        keys = sorted(int(key) for key in self.tank)
        if not 1 <= len(keys) <= 6:
            raise ValueError("Axiom 1 failed: tank must contain between 1 and 6 entries.")
        if keys != list(range(1, len(keys) + 1)):
            raise ValueError(
                "Axiom 1 failed: tank keys must be contiguous integer strings starting at 1."
            )
        return self
