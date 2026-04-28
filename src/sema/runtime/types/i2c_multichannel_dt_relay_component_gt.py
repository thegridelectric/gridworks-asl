from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.relay_actor_config import RelayActorConfig


class I2cMultichannelDtRelayComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.multichannel.dt.relay.component.gt/004"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig]
    display_name: str | None = None
    hw_uid: str | None = None
    i2c_bus: SpaceheatName
    i2c_address_list: list[StrictInt]
    type_name: Literal["i2c.multichannel.dt.relay.component.gt"] = "i2c.multichannel.dt.relay.component.gt"
    version: Literal["004"] = "004"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cMultichannelDtRelayComponentGt":
        """
        Axiom 1: ActorAndRelayIndexUniqueness
        ConfigList SHALL NOT contain duplicate ActorName values or duplicate RelayIdx values.
        """
        actor_names = [cfg.actor_name for cfg in self.config_list]
        relay_idxs = [cfg.relay_idx for cfg in self.config_list]
        if len(set(actor_names)) != len(actor_names):
            raise ValueError("Axiom 1 failed: config_list contains duplicate actor_name values.")
        if len(set(relay_idxs)) != len(relay_idxs):
            raise ValueError("Axiom 1 failed: config_list contains duplicate relay_idx values.")
        return self
