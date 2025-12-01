from typing import Optional

from gwasl.registry.base import AslType
from pydantic import PositiveInt,  model_validator
from typing_extensions import Self


from gwasl.registry.property_format import (
    SpaceheatName,
)


class ChannelConfig(AslType):
    ChannelName: SpaceheatName
    PollPeriodMs: Optional[PositiveInt] = None
    CapturePeriodS: PositiveInt
    AsyncCapture: bool
    AsyncCaptureDelta: Optional[PositiveInt] = None
    TypeName: str = "channel.config"
    Version: str = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: Capture and Polling Consistency.
        CapturePeriodMs (CapturePeriodS * 1000) must be larger than PollPeriodMs. If CapturePeriodMs < 10 * PollPeriodMs then CapturePeriodMs must be a multiple of PollPeriodMs.
        """
        # Implement check for axiom 1"
        return self
