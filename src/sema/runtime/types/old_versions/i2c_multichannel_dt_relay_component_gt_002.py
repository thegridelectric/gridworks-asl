from typing import Literal

from pydantic import ConfigDict, StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.relay_actor_config_002 import RelayActorConfig002
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import I2cMultichannelDtRelayComponentGt as I2cMultichannelDtRelayComponentGt003


class I2cMultichannelDtRelayComponentGt002(SemaType):
    """Sema: https://schemas.electricity.works/types/i2c.multichannel.dt.relay.component.gt/002"""

    component_id: UUID4Str
    component_attribute_class_id: UUID4Str
    config_list: list[RelayActorConfig002]
    display_name: str | None = None
    hw_uid: str | None = None
    i2c_address_list: list[StrictInt]
    type_name: Literal["i2c.multichannel.dt.relay.component.gt"] = "i2c.multichannel.dt.relay.component.gt"
    version: Literal["002"] = "002"

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def check_axiom_1(self) -> "I2cMultichannelDtRelayComponentGt002":
        actor_names = [cfg.actor_name for cfg in self.config_list]
        relay_idxs = [cfg.relay_idx for cfg in self.config_list]
        if len(set(actor_names)) != len(actor_names):
            raise ValueError("Axiom 1 failed: config_list contains duplicate actor_name values.")
        if len(set(relay_idxs)) != len(relay_idxs):
            raise ValueError("Axiom 1 failed: config_list contains duplicate relay_idx values.")
        return self

    def upgrade(self) ->I2cMultichannelDtRelayComponentGt003:
        """002 -> 003: upgrade nested RelayActorConfig items"""

        data = self.model_dump()

        # Upgrade nested configs
        upgraded_configs = []
        for cfg in self.config_list:
            if isinstance(cfg, RelayActorConfig002):
                upgraded_configs.append(cfg.upgrade())
            else:
                # Already latest or unexpected — keep as-is
                upgraded_configs.append(cfg)

        data["config_list"] = upgraded_configs

        # Update version
        data["version"] = "003"

        return I2cMultichannelDtRelayComponentGt003.model_validate(data)