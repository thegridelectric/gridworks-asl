from typing import Literal

from pydantic import ConfigDict, model_validator

from sema.registry.base import SemaType
from sema.registry.property_format import UUID4Str
from sema.registry.types.relay_actor_config import RelayActorConfig


class I2cMultichannelDtRelayComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.multichannel.dt.relay.component.gt/002"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    i2c_address_list: list[int]
    type_name: Literal["i2c.multichannel.dt.relay.component.gt"] = "i2c.multichannel.dt.relay.component.gt"
    version: Literal["002"] = "002"

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cMultichannelDtRelayComponentGt":
        actor_names = [cfg.actor_name for cfg in self.config_list]
        relay_idxs = [cfg.relay_idx for cfg in self.config_list]
        if len(set(actor_names)) != len(actor_names):
            raise ValueError("Axiom 1 failed: config_list contains duplicate actor_name values.")
        if len(set(relay_idxs)) != len(relay_idxs):
            raise ValueError("Axiom 1 failed: config_list contains duplicate relay_idx values.")
        return self
