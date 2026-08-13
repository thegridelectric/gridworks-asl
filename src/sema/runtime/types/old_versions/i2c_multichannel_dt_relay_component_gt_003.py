from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.old_versions.relay_actor_config_002 import RelayActorConfig002


class I2cMultichannelDtRelayComponentGt003(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.multichannel.dt.relay.component.gt/003"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig002]
    display_name: str | None = None
    hw_uid: str | None = None
    i2c_bus: SpaceheatName
    i2c_address_list: list[StrictInt]
    type_name: Literal["i2c.multichannel.dt.relay.component.gt"] = (
        "i2c.multichannel.dt.relay.component.gt"
    )
    version: Literal["003"] = "003"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cMultichannelDtRelayComponentGt003":
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

    def upgrade(self) -> I2cMultichannelDtRelayComponentGt:
        """
        - AsyncCaptureDelta: ConfigList[0] example now sets it explicitly (the
          relay.actor.config dependency itself is unchanged from 003: :002)
        - ComponentAttributeClassId (cac UUID) -> DeviceType (gw1.device.type value, pascal.case).
          Context-dependent: the device type lived on the referenced cac, not the component.
        """
        raise SemaType.upgrade_requires_context(
            "I2cMultichannelDtRelayComponentGt003 cannot be upgraded to "
            "I2cMultichannelDtRelayComponentGt without the source layout "
            "context: DeviceType is derived from the cac the component "
            "referenced, which the standalone component does not carry."
        )
