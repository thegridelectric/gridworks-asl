from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cAdcType
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt


class I2cAdcConfig(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.adc.config/000"""

    name: PascalCase
    i2c_bus: PascalCase
    i2c_address: NonNegativeInt
    adc_type: I2cAdcType
    channels: PositiveInt
    type_name: Literal["i2c.adc.config"] = "i2c.adc.config"
    version: Literal["000"] = "000"
