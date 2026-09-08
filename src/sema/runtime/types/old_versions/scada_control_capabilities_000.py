from typing import Literal
from pydantic import BaseModel, ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_actor_class_009 import Gw1ActorClass009
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.old_versions.i2c_multichannel_dt_relay_component_gt_002 import (
    I2cMultichannelDtRelayComponentGt002,
)
from sema.runtime.types.old_versions.scada_control_capabilities_001 import (
    ScadaControlCapabilities001,
)


class RelayNodesItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )

    name: SpaceheatName
    actor_class: Gw1ActorClass009
    display_name: str | None = None


class DacNodesItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )

    name: SpaceheatName
    actor_class: Gw1ActorClass009
    display_name: str | None = None


class ControlChannelsItem(BaseModel):
    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )

    name: str
    about_node_name: SpaceheatName


class ScadaControlCapabilities000(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.control.capabilities/000"""

    from_g_node_alias: LeftRightDot
    message_created_ms: UTCMilliseconds
    relay_nodes: list[RelayNodesItem]
    dac_nodes: list[DacNodesItem]
    control_channels: list[ControlChannelsItem]
    i2c_relay_component: I2cMultichannelDtRelayComponentGt002
    type_name: Literal["scada.control.capabilities"] = "scada.control.capabilities"
    version: Literal["000"] = "000"

    def upgrade(self) -> ScadaControlCapabilities001:
        """
        - RelayNodes[]: inline object -> spaceheat.node.gt:302
        - DacNodes[]: inline object -> spaceheat.node.gt:302
        - ControlChannels[]: inline object -> data.channel.gt:003
        - I2cRelayComponent dropped; CommandNodes[] (spaceheat.node.gt:302)
          and CommandInterfaces[] (gw.command.interface:000) added: the
          message is the cover of the command tree, one interface per node
          the root commands directly
        - Axioms: add control surface consistency checks
        """
        raise SemaType.upgrade_requires_context(
            "ScadaControlCapabilities000 cannot be upgraded to "
            "ScadaControlCapabilities001 without the source "
            "layout context needed to supply SpaceheatNodeGt.Handle, "
            "SpaceheatNodeGt.ShNodeId, DataChannelGt.Id, and related channel fields."
        )
