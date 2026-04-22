from typing import Literal

from pydantic import model_validator
from pydantic import StrictInt

from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_actor_class_009 import Gw1ActorClass009
from sema.runtime.property_format import HandleName, SpaceheatName, UUID4Str
from sema.runtime.types.old_versions.spaceheat_node_gt_300 import (
    SpaceheatNodeGt300,
)


class SpaceheatNodeGt200(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.node.gt/200"""

    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: str
    display_name: str | None = None
    component_id: str | None = None
    nameplate_power_w: StrictInt | None = None
    in_power_metering: bool | None = None
    sh_node_id: UUID4Str
    type_name: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    version: Literal["200"] = "200"

    model_config = dict(SemaType.model_config)
    model_config["extra"] = "allow"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SpaceheatNodeGt200":
        """
        Axiom 1: InPowerMeteringRequiresNameplate.
        If InPowerMetering is true, NameplatePowerW SHALL be present.
        """
        if self.in_power_metering and self.nameplate_power_w is None:
            raise ValueError("Axiom 1 failed: if in_power_metering is true, nameplate_power_w must be present.")
        return self

    def upgrade(self) -> SpaceheatNodeGt300:
        """
        200 -> 300:
        - ActorClass: string -> gw1.actor.class:009
        """
        data = self.model_dump()
        data["actor_class"] = Gw1ActorClass009(data["actor_class"]).value
        data["version"] = "300"
        return SpaceheatNodeGt300.model_validate(data)
