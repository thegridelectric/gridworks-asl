from typing import Any, Literal

from pydantic import field_validator
from pydantic import StrictInt

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_actor_class import Gw1ActorClass
from sema.runtime.enums.old_versions.gw1_actor_class_009 import Gw1ActorClass009
from sema.runtime.property_format import HandleName, SpaceheatName, UUID4Str
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt as SpaceheatNodeGt301


class SpaceheatNodeGt300(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.node.gt/300"""

    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: Gw1ActorClass009
    display_name: str | None = None
    component_id: UUID4Str | None = None
    nameplate_power_w: StrictInt | None = None
    in_power_metering: bool | None = None
    sh_node_id: UUID4Str
    type_name: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    version: Literal["300"] = "300"

    model_config = dict(SemaType.model_config)
    model_config["extra"] = "allow"

    @field_validator("actor_class", mode="before")
    @classmethod
    def coerce_actor_class_to_009(cls, value: Any) -> Any:
        if isinstance(value, Gw1ActorClass009):
            return value
        if isinstance(value, str) and value in Gw1ActorClass009.values():
            return value
        return Gw1ActorClass009.default().value

    def upgrade(self) -> SpaceheatNodeGt301:
        """
        300 -> 301:
        - BoardComponentId: add as Optional
        - ActorClass: gw1.actor.class:009 -> 011
        """
        data = self.model_dump()
        data["version"] = "301"
        return SpaceheatNodeGt301.model_validate(data)
