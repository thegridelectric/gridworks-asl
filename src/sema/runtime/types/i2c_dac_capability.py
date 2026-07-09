from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import I2cDacType
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt


class I2cDacCapability(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.dac.capability/000"""

    dac_name: PascalCase
    i2c_bus: PascalCase
    i2c_address: NonNegativeInt
    dac_type: I2cDacType
    channels: PositiveInt
    type_name: Literal["i2c.dac.capability"] = "i2c.dac.capability"
    version: Literal["000"] = "000"
