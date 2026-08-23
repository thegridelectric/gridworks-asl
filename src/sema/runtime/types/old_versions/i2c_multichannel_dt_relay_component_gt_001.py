from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.i2c_multichannel_dt_relay_component_gt_002 import (
    I2cMultichannelDtRelayComponentGt002,
)
from sema.runtime.types.old_versions.relay_actor_config_001 import RelayActorConfig001


class I2cMultichannelDtRelayComponentGt001(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.multichannel.dt.relay.component.gt/001"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig001]
    display_name: str | None = None
    hw_uid: str | None = None
    i2c_address_list: list[StrictInt]
    type_name: Literal["i2c.multichannel.dt.relay.component.gt"] = (
        "i2c.multichannel.dt.relay.component.gt"
    )
    version: Literal["001"] = "001"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cMultichannelDtRelayComponentGt001":
        """
        Axiom 1: ActorAndRelayIndexUniqueness
        ConfigList SHALL NOT contain duplicate ActorName values or duplicate RelayIdx values.
        """
        actor_names = [cfg.actor_name for cfg in self.config_list]
        relay_idxs = [cfg.relay_idx for cfg in self.config_list]
        if len(set(actor_names)) != len(actor_names):
            raise ValueError(
                "Axiom 1 failed: config_list contains duplicate actor_name values."
            )
        if len(set(relay_idxs)) != len(relay_idxs):
            raise ValueError(
                "Axiom 1 failed: config_list contains duplicate relay_idx values."
            )
        return self

    def upgrade(self) -> I2cMultichannelDtRelayComponentGt002:
        """
        - ConfigList element: relay.actor.config 001 -> 002
        """
        raise SemaType.upgrade_requires_context(
            "I2cMultichannelDtRelayComponentGt001 cannot be "
            "upgraded to I2cMultichannelDtRelayComponentGt002 "
            "without context: its ConfigList elements upgrade relay.actor.config "
            "001 -> 002, which adds the required DeEnergizedState / EnergizedState "
            "that SHALL NOT be fabricated."
        )
