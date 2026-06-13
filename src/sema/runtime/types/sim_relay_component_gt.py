from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.relay_actor_config import RelayActorConfig


class SimRelayComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/sim.relay.component.gt/000"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["sim.relay.component.gt"] = "sim.relay.component.gt"
    version: Literal["000"] = "000"
