from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName


class DfrConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/dfr.config/000"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    output_idx: PositiveInt
    initial_volts_times100: StrictInt
    type_name: Literal["dfr.config"] = "dfr.config"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DfrConfig":
        """
        Axiom 1: CaptureAndPollingConsistency
        If PollPeriodMs exists, then CapturePeriodMs (CapturePeriodS * 1000) must be larger
        than PollPeriodMs. If CapturePeriodMs is less than 10 * PollPeriodMs, then
        CapturePeriodMs must be a multiple of PollPeriodMs.
        """
        raise NotImplementedError("Axiom 1 validation is not implemented.")
