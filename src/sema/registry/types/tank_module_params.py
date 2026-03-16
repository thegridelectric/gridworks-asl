from typing import Literal, Optional
from sema.registry.codec import SemaType
from pydantic import PositiveInt, model_validator
from typing_extensions import Self

from sema.registry.property_format import (
    SpaceheatName,
)


class TankModuleParams(SemaType):
    """
    Parameters expected by a GridWorks TankModule2
    """
    hw_uid: str
    actor_node_name: SpaceheatName
    pico_a_b: Optional[str] = None
    capture_period_s: PositiveInt
    samples: PositiveInt
    num_sample_averages: PositiveInt
    async_capture_delta_micro_volts: PositiveInt
    capture_offset_s: Optional[float] = None
    type_name: Literal["tank.module.params"] = "tank.module.params"
    version: str = "110"

    @model_validator(mode="after")
    def check_pico_a_b(self) -> Self:
        """
        Axiom 1: "If PicoAB exists it must be a or b"
        """
        if self.pico_a_b and self.pico_a_b not in ["a", "b"]:
            raise ValueError(
                f"Axiom 1: If PicoAB exists it must be a or b, not {self.pico_a_b}"
            )

        return self
