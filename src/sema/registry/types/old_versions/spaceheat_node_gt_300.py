from typing import Literal

from sema.registry.base import SemaType
from sema.registry.enums.gw1_actor_class import Gw1ActorClass
from sema.registry.property_format import HandleName, SpaceheatName, UUID4Str


class SpaceheatNodeGt300(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.node.gt/300"""

    name: SpaceheatName
    actor_hierarchy_name: HandleName | None = None
    handle: HandleName | None = None
    actor_class: Gw1ActorClass
    display_name: str | None = None
    component_id: UUID4Str | None = None
    nameplate_power_w: int | None = None
    in_power_metering: bool | None = None
    sh_node_id: UUID4Str
    type_name: Literal["spaceheat.node.gt"] = "spaceheat.node.gt"
    version: Literal["300"] = "300"

    model_config = dict(SemaType.model_config)
    model_config["extra"] = "allow"
