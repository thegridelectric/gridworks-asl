from typing import Literal

from sema.registry.enums.gw1_unit import Gw1Unit
from sema.registry.property_format import LeftRightDot, SpaceheatName, UUID4Str
from sema.registry.types.derived_channel_gt import DerivedChannelGt


class DerivedChannelGt000(DerivedChannelGt):
    """Sema: https://schemas.electricity.works/types/derived.channel.gt/000"""

    input_channel_names: list[SpaceheatName] = []
    emission_method: str = "OnTrigger"
    output_unit: Gw1Unit | None = None
    type_name: Literal["derived.channel.gt"] = "derived.channel.gt"
    version: Literal["000"] = "000"
