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
