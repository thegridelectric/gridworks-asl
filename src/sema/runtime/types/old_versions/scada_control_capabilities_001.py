from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_actor_class_012 import Gw1ActorClass012
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.gw_command_interface import GwCommandInterface
from sema.runtime.types.old_versions.spaceheat_node_gt_302 import SpaceheatNodeGt302
from sema.runtime.types.scada_control_capabilities import ScadaControlCapabilities


class ScadaControlCapabilities001(SemaType):
    """Sema: https://schemas.electricity.works/types/scada.control.capabilities/001"""

    from_g_node_alias: LeftRightDot
    message_created_ms: UTCMilliseconds
    relay_nodes: list[SpaceheatNodeGt302]
    dac_nodes: list[SpaceheatNodeGt302]
    command_nodes: list[SpaceheatNodeGt302]
    control_channels: list[DataChannelGt]
    command_interfaces: list[GwCommandInterface]
    type_name: Literal["scada.control.capabilities"] = "scada.control.capabilities"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ScadaControlCapabilities001":
        """
        Axiom 1: ActorClassConsistency
        a. All nodes in RelayNodes SHALL have ActorClass equal to Relay.
        b. All nodes in DacNodes SHALL have ActorClass equal to ZeroTenOutputer.
        c. No node in CommandNodes SHALL have ActorClass equal to Relay or ZeroTenOutputer.
        """
        actuator_classes = {
            Gw1ActorClass012.Relay,
            Gw1ActorClass012.ZeroTenOutputer,
        }
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
        for node in self.command_nodes:
            if node.actor_class in actuator_classes:
                raise ValueError(
                    "Axiom 1 failed: command_nodes actor_class must not be Relay or "
                    "ZeroTenOutputer."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "ScadaControlCapabilities001":
        """
        Axiom 2: HandleTerminalMatchesName
        For every node in RelayNodes, DacNodes and CommandNodes, Handle SHALL be present
        and its final dot-separated token SHALL equal Name.
        """
        for node in [*self.relay_nodes, *self.dac_nodes, *self.command_nodes]:
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
    def check_axiom_3(self) -> "ScadaControlCapabilities001":
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
    def check_axiom_4(self) -> "ScadaControlCapabilities001":
        """
        Axiom 4: CommandInterfacesCoverTheTree
        a. The set of CommandInterfaces.ActorName values SHALL equal the set of Name
        values of the nodes in RelayNodes and CommandNodes whose Handle does not extend
        the Handle of any CommandNodes entry (a Handle extends another when it equals
        that Handle followed by a dot and further tokens).
        b. No two CommandInterfaces entries SHALL share an ActorName.
        """
        owner_prefixes = [
            f"{node.handle}." for node in self.command_nodes if node.handle is not None
        ]
        directly_commanded = {
            node.name
            for node in [*self.relay_nodes, *self.command_nodes]
            if node.handle is not None
            and not any(str(node.handle).startswith(p) for p in owner_prefixes)
        }
        interface_names = [
            interface.actor_name for interface in self.command_interfaces
        ]
        if set(interface_names) != directly_commanded:
            raise ValueError(
                "Axiom 4 failed: command_interfaces actor_name values must equal the "
                "names of the relay and command nodes the root commands directly."
            )
        if len(interface_names) != len(set(interface_names)):
            raise ValueError(
                "Axiom 4 failed: command_interfaces actor_name values must be unique."
            )
        return self

    def upgrade(self) -> ScadaControlCapabilities:
        """
        - RelayNodes[], DacNodes[], CommandNodes[]: spaceheat.node.gt:302 -> 303
        - A node may carry more than one CommandInterfaces entry, one per
          command vocabulary (five-v-boss: turn.5v.on.off and reboot.picos)
        """
        data = self.model_dump()
        for key in ("relay_nodes", "dac_nodes", "command_nodes"):
            for node in data[key]:
                node["version"] = "303"
        data["version"] = "002"
        return ScadaControlCapabilities.model_validate(data)
