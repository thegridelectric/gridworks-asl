from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str


class I2cReadBytes(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.read.bytes/000"""

    bus: SpaceheatName
    i2c_address: NonNegativeInt
    num_bytes: PositiveInt
    trigger_id: UUID4Str
    type_name: Literal["i2c.read.bytes"] = "i2c.read.bytes"
    version: Literal["000"] = "000"
