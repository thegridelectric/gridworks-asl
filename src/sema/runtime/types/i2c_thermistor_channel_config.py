from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cAdcChannel
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName


class I2cThermistorChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.channel.config/000"""

    channel_name: SpaceheatName
    poll_period_ms: PositiveInt | None = None
    capture_period_s: PositiveInt
    async_capture: bool
    async_capture_delta: PositiveInt | None = None
    exponent: StrictInt
    unit: SpaceheatUnit
    adc_channel: I2cAdcChannel
    send_to_derived: bool = False
    thermistor_beta: PositiveInt
    type_name: Literal["i2c.thermistor.channel.config"] = "i2c.thermistor.channel.config"
    version: Literal["000"] = "000"
