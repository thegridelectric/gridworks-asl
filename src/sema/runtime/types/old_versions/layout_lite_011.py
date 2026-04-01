from typing import Literal

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_seasonal_storage_mode import Gw1SeasonalStorageMode
from sema.runtime.enums.gw1_system_mode import Gw1SystemMode
from sema.runtime.property_format import (
    LeftRightDot,
    PositiveInt,
    UTCMilliseconds,
    UUID4Str,
)
from sema.runtime.types.ha1_params import Ha1Params
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import I2cMultichannelDtRelayComponentGt
from sema.runtime.types.old_versions.data_channel_gt_001 import DataChannelGt001
from sema.runtime.types.old_versions.derived_channel_gt_000 import DerivedChannelGt000
from sema.runtime.types.old_versions.spaceheat_node_gt_300 import SpaceheatNodeGt300
from sema.runtime.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import SimPicoTankModuleComponentGt

from sema.runtime.types.old_versions.layout_lite_012 import  LayoutLite012

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

    def upgrade(self) -> LayoutLite012:
        """
        - DerivedChannels[]: derived.channel.gt:000 → 001
        - DataChannels[]: data.channel.gt:001 → 002
        - ShNodes[]: spaceheat.node.gt:300 → 301
        - I2cRelayComponent: i2c.multichannel.dt.relay.component.gt:002 → 003
        - I2cRelayComponent: optional (was required)
        """

        data = self.model_dump()

        # ------------------------------------------------------------------
        # Apply only the required version transitions
        # ------------------------------------------------------------------

        # DerivedChannels[]
        data["derived_channels"] = [
            ch.upgrade()
            for ch in self.data_channels
        ]

        # DataChannels[]
        data["data_channels"] = [
            ch.upgrade()
            for ch in self.data_channels
        ]

        # ShNodes[]
        data["sh_nodes"] = [
            node.upgrade()
            for node in self.sh_nodes
        ]

        # I2cRelayComponent
        if self.i2c_relay_component is not None:
            data["i2c_relay_component"] = self.i2c_relay_component.upgrade()

        # ------------------------------------------------------------------
        # Version bump
        # ------------------------------------------------------------------

        data["version"] = "012"

        return LayoutLite012.model_validate(data)