from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.data_channel_gt_001 import DataChannelGt001
from sema.runtime.types.old_versions.ha1_params_000 import Ha1Params000
from sema.runtime.types.old_versions.layout_lite_002 import LayoutLite002
from sema.runtime.types.old_versions.pico_flow_module_component_gt_000 import (
    PicoFlowModuleComponentGt000,
)
from sema.runtime.types.old_versions.pico_tank_module_component_gt_000 import (
    PicoTankModuleComponentGt000,
)
from sema.runtime.types.old_versions.spaceheat_node_gt_200 import SpaceheatNodeGt200


class LayoutLite001(SemaType):
    """Sema: https://schemas.electricity.works/types/layout.lite/001"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    message_created_ms: UTCMilliseconds
    message_id: UUID4Str
    strategy: str
    zone_list: list[str]
    total_store_tanks: PositiveInt
    sh_nodes: list[SpaceheatNodeGt200]
    data_channels: list[DataChannelGt001]
    tank_module_components: list[PicoTankModuleComponentGt000]
    flow_module_components: list[PicoFlowModuleComponentGt000]
    ha1_params: Ha1Params000
    type_name: Literal["layout.lite"] = "layout.lite"
    version: Literal["001"] = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "LayoutLite001":
        """
        Axiom 1: DcNodeConsistency
        Every DataChannels.AboutNodeName and DataChannels.CapturedByNodeName SHALL reference
        an existing ShNodes.Name, and every captured-by node SHALL have an active
        ActorClass.
        """
        node_names = {node.name for node in self.sh_nodes}
        active_actorless = {"NoActor"}
        for channel in self.data_channels:
            if (
                channel.about_node_name not in node_names
                or channel.captured_by_node_name not in node_names
            ):
                raise ValueError(
                    "Axiom 1 failed: data channel node references must exist in sh_nodes."
                )
            captured = next(
                node
                for node in self.sh_nodes
                if node.name == channel.captured_by_node_name
            )
            if str(captured.actor_class) in active_actorless:
                raise ValueError(
                    "Axiom 1 failed: captured-by node must have an active actor class."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "LayoutLite001":
        """
        Axiom 2: NodeHandleHierarchyConsistency
        Every ShNode with a dotted handle SHALL have its immediate boss present as another
        ShNode in the same payload.
        """
        node_names = {node.name for node in self.sh_nodes}
        for node in self.sh_nodes:
            if node.handle and "." in node.handle:
                immediate_boss = node.handle.split(".")[-2]
                if immediate_boss not in node_names:
                    raise ValueError(
                        "Axiom 2 failed: missing immediate boss node for handle hierarchy."
                    )
        return self

    def upgrade(self) -> LayoutLite002:
        """Historical back-fill from S3 wire evidence. As v003 but one window earlier: Ha1Params single ha1.params:001 (v002 first appears in v003), and I2cRelayComponent oneOf[i2c 001, 002] (deploy-lag union; i2c/relay.actor.config bumped to 002 on 2024-12-31)."""
        raise SemaType.upgrade_requires_context(
            "layout.lite:001 cannot be upgraded to layout.lite:002 without "
            "context: v002 adds the required I2cRelayComponent and upgrades "
            "Ha1Params ha1.params 000 -> 001 (adding the required MaxEwtF), "
            "neither derivable from a v001 message. JournalKeeper retains v001 "
            "messages at their own version."
        )
