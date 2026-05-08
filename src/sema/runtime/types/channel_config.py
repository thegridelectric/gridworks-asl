from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName


class ChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/channel.config/000"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    type_name: Literal["channel.config"] = "channel.config"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ChannelConfig":
        """
        Axiom 1: CaptureAndPollingConsistency
        If PollPeriodMs is present, then CapturePeriodMs (CapturePeriodS * 1000) SHALL be
        greater than PollPeriodMs. If CapturePeriodMs is less than 10 times PollPeriodMs, then
        CapturePeriodMs SHALL be a multiple of PollPeriodMs.
        """
        if self.poll_period_ms is None:
            return self

        capture_period_ms = self.capture_period_s * 1000
        if capture_period_ms <= self.poll_period_ms:
            raise ValueError(
                "Axiom 1 failed: capture_period_s * 1000 must be greater than poll_period_ms."
            )
        if (
            capture_period_ms < 10 * self.poll_period_ms
            and capture_period_ms % self.poll_period_ms != 0
        ):
            raise ValueError(
                "Axiom 1 failed: capture period must be a multiple of poll period when "
                "capture_period_ms is less than 10 times poll_period_ms."
            )
        return self
