from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.enums import ThermistorDataMethod
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.ads_channel_config import AdsChannelConfig


class AdsChannelConfig000(SemaType):
    """Sema: https://schemas.electricity.works/types/ads.channel.config/000"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    terminal_block_idx: PositiveInt
    thermistor_device_type: PascalCase
    data_processing_method: ThermistorDataMethod | None = None
    data_processing_description: str | None = None
    type_name: Literal["ads.channel.config"] = "ads.channel.config"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "AdsChannelConfig000":
        """
        Axiom 1: CaptureAndPollingConsistency
        If PollPeriodMs exists, then CapturePeriodMs (CapturePeriodS * 1000) must be larger
        than PollPeriodMs. If CapturePeriodMs is less than 10 * PollPeriodMs, then
        CapturePeriodMs must be a multiple of PollPeriodMs.
        """
        if self.poll_period_ms is not None:
            capture_ms = self.capture_period_s * 1000
            if not capture_ms > self.poll_period_ms:
                raise ValueError(
                    "Axiom 1 (CaptureAndPollingConsistency): CapturePeriodMs "
                    "must be larger than PollPeriodMs."
                )
            if (
                capture_ms < 10 * self.poll_period_ms
                and capture_ms % self.poll_period_ms != 0
            ):
                raise ValueError(
                    "Axiom 1 (CaptureAndPollingConsistency): CapturePeriodMs "
                    "must be a multiple of PollPeriodMs."
                )
        return self

    def upgrade(self) -> AdsChannelConfig:
        """
        - Unit: drop (redundant; unit and scaling are carried by channel identity)
        - Exponent: drop (redundant; unit and scaling are carried by channel identity)
        - CapturePeriodS / AsyncCapture / AsyncCaptureDelta / PollPeriodMs: drop
          (capture/report tuning moved to operational-params capture.tuning)
        """
        data = self.model_dump()
        del data["unit"]
        del data["exponent"]
        for key in (
            "capture_period_s",
            "async_capture",
            "async_capture_delta",
            "poll_period_ms",
        ):
            data.pop(key, None)
        data["version"] = "001"
        return AdsChannelConfig.model_validate(data)
