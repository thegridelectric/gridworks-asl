from typing import Literal
from pydantic import StrictFloat, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.tank_module_params import TankModuleParams


class TankModuleParams110(SemaType):
    """Sema: https://schemas.electricity.works/types/tank.module.params/110"""

    hw_uid: str
    actor_node_name: SpaceheatName
    pico_a_b: str | None = None
    capture_period_s: PositiveInt
    samples: PositiveInt
    num_sample_averages: PositiveInt
    async_capture_delta_micro_volts: PositiveInt
    capture_offset_s: StrictFloat | None = None
    type_name: Literal["tank.module.params"] = "tank.module.params"
    version: Literal["110"] = "110"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "TankModuleParams110":
        """
        Axiom 1: PicoABIsAOrB
        If PicoAB is present it SHALL be "a" or "b".
        """
        if self.pico_a_b is not None and self.pico_a_b not in ("a", "b"):
            raise ValueError(
                f"Axiom 1: If PicoAB is present it SHALL be a or b, not {self.pico_a_b!r}"
            )
        return self

    def upgrade(self) -> TankModuleParams:
        """
        - PicoBoardVariant: add
        - MicropythonVersion: add
        """
        raise SemaType.upgrade_requires_context(
            "TankModuleParams110 cannot be upgraded to "
            "TankModuleParams without context: v200 adds "
            "PicoBoardVariant and MicropythonVersion, which only the posting "
            "pico knows, and they SHALL NOT be fabricated."
        )
