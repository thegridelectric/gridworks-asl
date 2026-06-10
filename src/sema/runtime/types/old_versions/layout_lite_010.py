from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1SeasonalStorageMode
from sema.runtime.enums import Gw1SystemMode
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.gw1_tank_temp_calibration_map import Gw1TankTempCalibrationMap
from sema.runtime.types.old_versions.data_channel_gt_001 import DataChannelGt001
from sema.runtime.types.old_versions.derived_channel_gt_000 import DerivedChannelGt000
from sema.runtime.types.old_versions.ha1_params_005 import Ha1Params005
from sema.runtime.types.old_versions.i2c_multichannel_dt_relay_component_gt_002 import (
    I2cMultichannelDtRelayComponentGt002,
)
from sema.runtime.types.old_versions.layout_lite_011 import LayoutLite011
from sema.runtime.types.old_versions.spaceheat_node_gt_300 import SpaceheatNodeGt300
from sema.runtime.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


class LayoutLite010(SemaType):
    """Sema: https://schemas.electricity.works/types/layout.lite/010"""

    from_g_node_alias: LeftRightDot
    message_created_ms: UTCMilliseconds
    message_id: UUID4Str
    strategy: str
    system_mode: Gw1SystemMode
    seasonal_storage_mode: Gw1SeasonalStorageMode
    buffer_short_cycling: bool
    zone_list: list[str]
    critical_zone_list: list[str]
    total_store_tanks: PositiveInt
    sh_nodes: list[SpaceheatNodeGt300 | SpaceheatNodeGt]
    data_channels: list[DataChannelGt001]
    derived_channels: list[DerivedChannelGt000]
    tank_module_components: list[
        PicoTankModuleComponentGt | SimPicoTankModuleComponentGt
    ]
    flow_module_components: list[PicoFlowModuleComponentGt]
    ha1_params: Ha1Params005
    i2c_relay_component: I2cMultichannelDtRelayComponentGt002 | None = None
    t_map: Gw1TankTempCalibrationMap | None = None
    type_name: Literal["layout.lite"] = "layout.lite"
    version: Literal["010"] = "010"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "LayoutLite010":
        """
        Axiom 1: DcNodeConsistency
        Every DataChannels.AboutNodeName and DataChannels.CapturedByNodeName SHALL reference an
        existing ShNodes.Name, and every captured-by node SHALL have an active ActorClass.
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
    def check_axiom_2(self) -> "LayoutLite010":
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

    @model_validator(mode="after")
    def check_axiom_3(self) -> "LayoutLite010":
        """
        Axiom 3: CriticalZoneSubset
        CriticalZoneList SHALL be a subset of ZoneList.
        """
        if not set(self.critical_zone_list).issubset(set(self.zone_list)):
            raise ValueError(
                "Axiom 3 failed: critical_zone_list must be a subset of zone_list."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "LayoutLite010":
        """
        Axiom 4: DerivedNodeConsistency
        Every DerivedChannels.CreatedByNodeName SHALL reference an existing ShNodes.Name whose
        ActorClass is active.
        """
        nodes = {node.name: node for node in self.sh_nodes}
        for channel in self.derived_channels:
            created_by = nodes.get(channel.created_by_node_name)
            if created_by is None or str(created_by.actor_class) == "NoActor":
                raise ValueError(
                    "Axiom 4 failed: derived channel created_by_node_name must reference an active node."
                )
        return self

    def upgrade(self) -> LayoutLite011:
        """
        - Ha1Params: ha1.params:005 -> 006
        - DerivedChannels[]: derived.channel.gt:000 -> 000 | 001
        """
        data = self.model_dump()
        data["ha1_params"] = self.ha1_params.upgrade()
        data["version"] = "011"
        return LayoutLite011.model_validate(data)
