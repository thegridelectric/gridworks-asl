from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cDacChannel
from sema.runtime.enums import I2cDacVref
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PositiveInt


class I2cDacChannelConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.dac.channel.config/000"""

    dac_channel: I2cDacChannel
    power_on_raw_value: NonNegativeInt
    power_on_vref: I2cDacVref
    power_on_gain: PositiveInt
    type_name: Literal["i2c.dac.channel.config"] = "i2c.dac.channel.config"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cDacChannelConfig":
        """
        Axiom 1: EepromRanges
        a. PowerOnRawValue SHALL be less than 4096. b. PowerOnGain SHALL be 1 or 2.
        """
        if self.power_on_raw_value >= 4096:
            raise ValueError(
                "Axiom 1 (EepromRanges) failed: PowerOnRawValue "
                f"{self.power_on_raw_value} is not less than 4096."
            )
        if self.power_on_gain not in (1, 2):
            raise ValueError(
                "Axiom 1 (EepromRanges) failed: PowerOnGain "
                f"{self.power_on_gain} is not 1 or 2."
            )
        return self
