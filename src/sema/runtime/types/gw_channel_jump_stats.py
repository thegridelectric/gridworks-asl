from typing import Literal
from pydantic import StrictFloat, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PositiveFloat
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds


class GwChannelJumpStats(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.channel.jump.stats/000"""

    channel_name: SpaceheatName
    channel_type_name: LeftRightDot
    channel_version: str
    window_start_unix_ms: UTCMilliseconds
    window_end_unix_ms: UTCMilliseconds
    num_readings: NonNegativeInt
    jump_threshold: PositiveFloat
    max_gap_s: PositiveInt
    spike_count: NonNegativeInt
    max_abs_jump: StrictFloat
    median_abs_jump: StrictFloat
    type_name: Literal["gw.channel.jump.stats"] = "gw.channel.jump.stats"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwChannelJumpStats":
        """
        Axiom 1: WindowOrder
        WindowEndUnixMs SHALL be greater than WindowStartUnixMs.
        """
        if not self.window_end_unix_ms > self.window_start_unix_ms:
            raise ValueError(
                "Axiom 1 (WindowOrder) failed: WindowEndUnixMs must be greater "
                "than WindowStartUnixMs."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwChannelJumpStats":
        """
        Axiom 2: NonNegativeMagnitudes
        MaxAbsJump and MedianAbsJump SHALL each be greater than or equal to zero.
        """
        if self.max_abs_jump < 0 or self.median_abs_jump < 0:
            raise ValueError(
                "Axiom 2 (NonNegativeMagnitudes) failed: MaxAbsJump and "
                "MedianAbsJump must each be >= 0."
            )
        return self
