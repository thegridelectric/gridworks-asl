from typing import Literal

from pydantic import PositiveInt

from sema.registry.base import SemaType
from sema.registry.enums.gw1_seasonal_storage_mode import Gw1SeasonalStorageMode
from sema.registry.enums.gw1_system_mode import Gw1SystemMode
from sema.registry.property_format import LeftRightDot, UTCMilliseconds, UUID4Str
from sema.registry.types.ha1_params import Ha1Params
from sema.registry.types.i2c_multichannel_dt_relay_component_gt import I2cMultichannelDtRelayComponentGt
from sema.registry.types.old_versions.data_channel_gt_001 import DataChannelGt001
from sema.registry.types.old_versions.derived_channel_gt_000 import DerivedChannelGt000
from sema.registry.types.old_versions.spaceheat_node_gt_300 import SpaceheatNodeGt300
from sema.registry.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.registry.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.registry.types.sim_pico_tank_module_component_gt import SimPicoTankModuleComponentGt


class LayoutLite011(SemaType):
    """Sema: https://schemas.electricity.works/types/layout.lite/011"""

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
    sh_nodes: list[SpaceheatNodeGt300]
    data_channels: list[DataChannelGt001]
    derived_channels: list[DerivedChannelGt000]
    tank_module_components: list[PicoTankModuleComponentGt | SimPicoTankModuleComponentGt]
    flow_module_components: list[PicoFlowModuleComponentGt]
    ha1_params: Ha1Params
    i2c_relay_component: I2cMultichannelDtRelayComponentGt
    t_map: object | None = None
    type_name: Literal["layout.lite"] = "layout.lite"
    version: Literal["011"] = "011"

    def to_latest(self) -> "LayoutLite":
        from sema.registry.types.data_channel_gt import DataChannelGt  # noqa: PLC0415
        from sema.registry.types.derived_channel_gt import DerivedChannelGt  # noqa: PLC0415
        from sema.registry.types.layout_lite import LayoutLite  # noqa: PLC0415
        from sema.registry.types.spaceheat_node_gt import SpaceheatNodeGt  # noqa: PLC0415

        return LayoutLite(
            from_g_node_alias=self.from_g_node_alias,
            message_created_ms=self.message_created_ms,
            message_id=self.message_id,
            strategy=self.strategy,
            system_mode=self.system_mode,
            seasonal_storage_mode=self.seasonal_storage_mode,
            buffer_short_cycling=self.buffer_short_cycling,
            zone_list=self.zone_list,
            critical_zone_list=self.critical_zone_list,
            total_store_tanks=self.total_store_tanks,
            sh_nodes=[
                SpaceheatNodeGt(
                    name=node.name,
                    actor_hierarchy_name=node.actor_hierarchy_name,
                    handle=node.handle,
                    actor_class=node.actor_class,
                    display_name=node.display_name,
                    component_id=node.component_id,
                    nameplate_power_w=node.nameplate_power_w,
                    in_power_metering=node.in_power_metering,
                    sh_node_id=node.sh_node_id,
                )
                for node in self.sh_nodes
            ],
            data_channels=[
                DataChannelGt(
                    name=channel.name,
                    display_name=channel.display_name,
                    about_node_name=channel.about_node_name,
                    captured_by_node_name=channel.captured_by_node_name,
                    telemetry_name=channel.telemetry_name,
                    quantity=channel.quantity,
                    terminal_asset_alias=channel.terminal_asset_alias,
                    in_power_metering=channel.in_power_metering,
                    start_s=channel.start_s,
                    id=channel.id,
                )
                for channel in self.data_channels
            ],
            derived_channels=[
                DerivedChannelGt(
                    id=channel.id,
                    name=channel.name,
                    created_by_node_name=channel.created_by_node_name,
                    strategy=channel.strategy,
                    input_channel_names=channel.input_channel_names,
                    output_unit=channel.output_unit,
                    emission_method=channel.emission_method,
                    async_emit_delta=channel.async_emit_delta,
                    emit_period_s=channel.emit_period_s,
                    parameters=channel.parameters,
                    display_name=channel.display_name,
                    terminal_asset_alias=channel.terminal_asset_alias,
                )
                for channel in self.derived_channels
            ],
            tank_module_components=self.tank_module_components,
            flow_module_components=self.flow_module_components,
            ha1_params=self.ha1_params,
            i2c_relay_component=self.i2c_relay_component,
            t_map=self.t_map,
        )
