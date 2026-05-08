from typing import Literal
from pydantic import ConfigDict, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_actor_class_009 import Gw1ActorClass009
from sema.runtime.property_format import HandleName
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


class SpaceheatNodeGt300(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.node.gt/300"""

    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: Gw1ActorClass009
    display_name: str | None = None
    component_id: str | None = None
    nameplate_power_w: PositiveInt | None = None
    in_power_metering: bool | None = None
    sh_node_id: UUID4Str
    type_name: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    version: Literal["300"] = "300"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SpaceheatNodeGt300":
        """
        Axiom 1: InPowerMeteringRequiresNameplate
        If InPowerMetering is true, NameplatePowerW SHALL be present.
        """
        if self.in_power_metering and self.nameplate_power_w is None:
            raise ValueError(
                "Axiom 1 failed: nameplate_power_w is required when in_power_metering is true."
            )
        return self

    def upgrade(self) -> SpaceheatNodeGt:
        """
        - BoardComponentId: add as Optional
        - ActorClass: gw1.actor.class:009 -> 011
        """
        data = self.model_dump()
        data["version"] = "301"
        return SpaceheatNodeGt.model_validate(data)
