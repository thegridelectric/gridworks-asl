from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cAdcChannel
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.i2c_thermistor_channel_config import I2cThermistorChannelConfig


class I2cThermistorChannelConfig001(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.channel.config/001"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    adc_channel: I2cAdcChannel
    send_to_derived: bool
    thermistor_beta: PositiveInt
    type_name: Literal["i2c.thermistor.channel.config"] = (
        "i2c.thermistor.channel.config"
    )
    version: Literal["001"] = "001"

    def upgrade(self) -> I2cThermistorChannelConfig:
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
        data["version"] = "002"
        return I2cThermistorChannelConfig.model_validate(data)
