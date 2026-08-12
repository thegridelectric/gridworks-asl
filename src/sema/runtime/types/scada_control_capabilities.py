from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_actor_class_012 import Gw1ActorClass012
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.old_versions.i2c_multichannel_dt_relay_component_gt_002 import (
    I2cMultichannelDtRelayComponentGt002,
)
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


class ScadaControlCapabilities(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.control.capabilities/002"""

    from_g_node_alias: LeftRightDot
    message_created_ms: UTCMilliseconds
    relay_nodes: list[SpaceheatNodeGt]
    dac_nodes: list[SpaceheatNodeGt]
    control_channels: list[DataChannelGt]
    i2c_relay_component: I2cMultichannelDtRelayComponentGt002
    type_name: Literal["scada.control.capabilities"] = "scada.control.capabilities"
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ScadaControlCapabilities":
        """
        Axiom 1: ActorClassConsistency
        a. All nodes in RelayNodes SHALL have ActorClass equal to Relay.
        b. All nodes in DacNodes SHALL have ActorClass equal to ZeroTenOutputer.
        """
        for node in self.relay_nodes:
            if node.actor_class != Gw1ActorClass012.Relay:
                raise ValueError(
                    "Axiom 1 failed: every relay_nodes actor_class must be Relay."
                )
        for node in self.dac_nodes:
            if node.actor_class != Gw1ActorClass012.ZeroTenOutputer:
                raise ValueError(
                    "Axiom 1 failed: every dac_nodes actor_class must be ZeroTenOutputer."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "ScadaControlCapabilities":
        """
        Axiom 2: HandleTerminalMatchesName
        For every node in RelayNodes and DacNodes, Handle SHALL be present and its final
        dot-separated token SHALL equal Name.
        """
        for node in [*self.relay_nodes, *self.dac_nodes]:
            if node.handle is None:
                raise ValueError(
                    "Axiom 2 failed: every control node must have a handle."
                )
            if str(node.handle).split(".")[-1] != node.name:
                raise ValueError(
                    "Axiom 2 failed: every control node handle terminal token must equal name."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "ScadaControlCapabilities":
        """
        Axiom 3: AboutNodesAreControlNodes
        The set of ControlChannels.AboutNodeName values SHALL equal the set of
        RelayNodes.Name and DacNodes.Name values.
        """
        control_node_names = {
            node.name for node in [*self.relay_nodes, *self.dac_nodes]
        }
        channel_about_node_names = {
            channel.about_node_name for channel in self.control_channels
        }
        if channel_about_node_names != control_node_names:
            raise ValueError(
                "Axiom 3 failed: control_channels about_node_name values must equal "
                "relay_nodes and dac_nodes names."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "ScadaControlCapabilities":
        """
        Axiom 4: I2cRelayComponentChannelControlNodeConsistency
        a. The set of ActorName values in I2cRelayComponent.ConfigList SHALL equal the set
        of RelayNodes.Name values.
        b. For each relay actor config in I2cRelayComponent.ConfigList, ChannelName SHALL
        equal the Name of the ControlChannels entry whose AboutNodeName is that relay actor
        config's ActorName.
        """
        relay_node_names = {node.name for node in self.relay_nodes}
        config_actor_names = {
            config.actor_name for config in self.i2c_relay_component.config_list
        }
        if config_actor_names != relay_node_names:
            raise ValueError(
                "Axiom 4 failed: i2c_relay_component config_list actor_name values "
                "must equal relay_nodes names."
            )

        channel_by_about_node_name = {
            channel.about_node_name: channel for channel in self.control_channels
        }
        for config in self.i2c_relay_component.config_list:
            channel = channel_by_about_node_name.get(config.actor_name)
            if channel is None or config.channel_name != channel.name:
                raise ValueError(
                    "Axiom 4 failed: every relay config channel_name must match the "
                    "control channel name for its actor_name."
                )
        return self
