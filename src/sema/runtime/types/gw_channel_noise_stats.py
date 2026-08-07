from typing import Literal
from pydantic import StrictFloat, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import NonEmptyString
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds


class GwChannelNoiseStats(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.channel.noise.stats/000"""

    channel_name: SpaceheatName
    channel_type_name: LeftRightDot
    channel_version: str
    condition_label: NonEmptyString | None = None
    window_start_unix_ms: UTCMilliseconds
    window_end_unix_ms: UTCMilliseconds
    num_samples: PositiveInt
    mean: StrictFloat
    sd: StrictFloat
    p2p: StrictFloat
    type_name: Literal["gw.channel.noise.stats"] = "gw.channel.noise.stats"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwChannelNoiseStats":
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
    def check_axiom_2(self) -> "GwChannelNoiseStats":
        """
        Axiom 2: NonNegativeSpread
        Sd and P2p SHALL each be greater than or equal to zero.
        """
        if self.sd < 0 or self.p2p < 0:
            raise ValueError(
                "Axiom 2 (NonNegativeSpread) failed: Sd and P2p must each be >= 0."
            )
        return self
