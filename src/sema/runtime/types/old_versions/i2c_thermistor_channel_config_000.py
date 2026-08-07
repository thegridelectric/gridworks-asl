from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cAdcChannel
from sema.runtime.enums import SpaceheatUnit
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.types.old_versions.i2c_thermistor_channel_config_001 import (
    I2cThermistorChannelConfig001,
)


class I2cThermistorChannelConfig000(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.thermistor.channel.config/000"""

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
    version: Literal["000"] = "000"

    def upgrade(self) -> I2cThermistorChannelConfig001:
        """
        Structural-only restamp of the field-emitted shape (see 000).
        """
        data = self.model_dump()
        data["version"] = "001"
        return I2cThermistorChannelConfig001.model_validate(data)
