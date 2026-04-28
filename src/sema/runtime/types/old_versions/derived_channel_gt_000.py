from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1EmissionMethod
from sema.runtime.enums.old_versions.gw1_unit_000 import Gw1Unit000
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.derived_channel_gt_001 import DerivedChannelGt001


class DerivedChannelGt000(SemaType):
    """Sema: https://schemas.electricity.works/types/derived.channel.gt/000"""

    id: UUID4Str
    name: SpaceheatName
    created_by_node_name: SpaceheatName
    strategy: SpaceheatName
    output_unit: Gw1Unit000 | None = None
    display_name: str
    terminal_asset_alias: LeftRightDot
    type_name: Literal["derived.channel.gt"] = "derived.channel.gt"
    version: Literal["000"] = "000"

    def upgrade(self) -> DerivedChannelGt001:
        """
        - InputChannelNames[]: add
        - EmissionMethod: add
        - Parameters: add (Optional)
        """

        data = self.model_dump()
        data["input_channel_names"] = []
        data["emission_method"] = Gw1EmissionMethod.OnTrigger
        data["parameters"] = None
        data["version"] = "001"
        return DerivedChannelGt001.model_validate(data)
