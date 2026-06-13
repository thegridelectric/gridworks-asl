from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.relay_actor_config import RelayActorConfig


class Gw108VdcRelayComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw108.vdc.relay.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig]
    gpio_pin: PositiveInt
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["gw108.vdc.relay.component.gt"] = "gw108.vdc.relay.component.gt"
    version: Literal["001"] = "001"
