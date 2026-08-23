from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.data_channel_gt_001 import DataChannelGt001
from sema.runtime.types.old_versions.ha1_params_001 import Ha1Params001
from sema.runtime.types.old_versions.i2c_multichannel_dt_relay_component_gt_001 import (
    I2cMultichannelDtRelayComponentGt001,
)
from sema.runtime.types.old_versions.i2c_multichannel_dt_relay_component_gt_002 import (
    I2cMultichannelDtRelayComponentGt002,
)
from sema.runtime.types.old_versions.layout_lite_003 import LayoutLite003
from sema.runtime.types.old_versions.pico_flow_module_component_gt_000 import (
    PicoFlowModuleComponentGt000,
)
from sema.runtime.types.old_versions.pico_tank_module_component_gt_000 import (
    PicoTankModuleComponentGt000,
)
from sema.runtime.types.old_versions.spaceheat_node_gt_200 import SpaceheatNodeGt200
from sema.runtime.types.synth_channel_gt import SynthChannelGt


class LayoutLite002(SemaType):
    """Sema: https://schemas.electricity.works/types/layout.lite/002"""

    from_g_node_alias: LeftRightDot
    from_g_node_instance_id: UUID4Str
    message_created_ms: UTCMilliseconds
    message_id: UUID4Str
    strategy: str
    zone_list: list[str]
    total_store_tanks: PositiveInt
    sh_nodes: list[SpaceheatNodeGt200]
    data_channels: list[DataChannelGt001]
    synth_channels: list[SynthChannelGt] | None = None
    tank_module_components: list[PicoTankModuleComponentGt000]
    flow_module_components: list[PicoFlowModuleComponentGt000]
    ha1_params: Ha1Params001
    i2c_relay_component: (
        I2cMultichannelDtRelayComponentGt001 | I2cMultichannelDtRelayComponentGt002
    )
    type_name: Literal["layout.lite"] = "layout.lite"
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "LayoutLite002":
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
    def check_axiom_2(self) -> "LayoutLite002":
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

    def upgrade(self) -> LayoutLite003:
        """Historical back-fill from S3 wire evidence. As v004 but the deploy-lag unions sit one window earlier: Ha1Params oneOf[001, 002]; TankModuleComponents single pico.tank 000 (v010 first appears in v004)."""
        raise SemaType.upgrade_requires_context(
            "layout.lite:002 cannot be upgraded to layout.lite:003 without context: "
            "003 pins I2cRelayComponent at i2c:002, but a v002 message may carry "
            "i2c:001 (whose 001->002 upgrade requires context -- it adds the required "
            "DeEnergizedState/EnergizedState under relay.actor.config). JournalKeeper "
            "retains v002 messages at their own version."
        )
