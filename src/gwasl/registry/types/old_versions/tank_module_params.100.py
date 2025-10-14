"""Type tank.module.params, version 100"""

from typing import Literal, Optional
from gwasl.registry.codec import AslType
from pydantic import PositiveInt, field_validator

from gwasl.registry.property_format import (
    SpaceheatName,
)
from gwasl.registry.types import TankModuleParams

class TankModuleParams100(AslType):
    """
    Parameters expected by a GridWorks TankModule2
    """

    hw_uid: str
    actor_node_name: SpaceheatName
    pico_a_b: str
    capture_period_s: PositiveInt
    samples: PositiveInt
    num_sample_averages: PositiveInt
    async_capture_delta_micro_volts: PositiveInt
    capture_offset_s: Optional[float] = None
    type_name: Literal["tank.module.params"] = "tank.module.params"
    version: str = "100"

    @field_validator("PicoAB")
    @classmethod
    def check_pico_a_b(cls, v: str) -> str:
        """
        Axiom 1: "PicoAB must be a or b"
        """
        # Implement Axiom(s)
        return v

    def to_latest(self) -> "TankModuleParams":
        """Convert to the latest version 110. 
        Only difference is that pico_a_b is optional
        in latest.
        """
        return TankModuleParams.from_dict(self.to_dict())
