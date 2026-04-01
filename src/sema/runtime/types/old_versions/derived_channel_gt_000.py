from typing import Any, Literal

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_emission_method import Gw1EmissionMethod
from sema.runtime.enums.gw1_unit import Gw1Unit
from sema.runtime.property_format import LeftRightDot, SpaceheatName, UUID4Str
from sema.runtime.types.derived_channel_gt import DerivedChannelGt


class DerivedChannelGt000(SemaType):
    """Sema: https://schemas.electricity.works/types/derived.channel.gt/000"""

    id: UUID4Str
    name: SpaceheatName
    created_by_node_name: SpaceheatName
    strategy: SpaceheatName
    output_unit: Gw1Unit | None = None
    display_name: str
    terminal_asset_alias: LeftRightDot
    type_name: Literal["derived.channel.gt"] = "derived.channel.gt"
    version: Literal["000"] = "000"

    def upgrade(self) -> DerivedChannelGt:
        """000 -> 001: add InputChannelNames, EmissionMethod, and Parameters."""

        data = self.model_dump()
        data["input_channel_names"] = []
        data["emission_method"] = Gw1EmissionMethod.OnTrigger
        data["parameters"] = None
        data["version"] = "001"
        return DerivedChannelGt.model_validate(data)
