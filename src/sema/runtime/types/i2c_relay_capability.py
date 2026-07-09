from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import RelayWiringConfig
from sema.runtime.property_format import NonNegativeInt
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt


class I2cRelayCapability(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.relay.capability/000"""

    relay_name: PascalCase
    expander_idx: PositiveInt
    register_index: NonNegativeInt
    bit_index: NonNegativeInt
    supported_wiring_configs: list[RelayWiringConfig]
    notes: str | None = None
    type_name: Literal["i2c.relay.capability"] = "i2c.relay.capability"
    version: Literal["000"] = "000"
