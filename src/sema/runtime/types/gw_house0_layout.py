from typing import Any, Literal
from sema.runtime.base import SemaType
from sema.runtime.types.ads111x_based_component_gt import Ads111xBasedComponentGt
from sema.runtime.types.ads111x_based_device_type_gt import Ads111xBasedDeviceTypeGt
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.derived_channel_gt import DerivedChannelGt
from sema.runtime.types.dfr_component_gt import DfrComponentGt
from sema.runtime.types.electric_meter_component_gt import ElectricMeterComponentGt
from sema.runtime.types.electric_meter_device_type_gt import ElectricMeterDeviceTypeGt
from sema.runtime.types.g_node_gt import GNodeGt
from sema.runtime.types.gw1_scada_device_type_gt import Gw1ScadaDeviceTypeGt
from sema.runtime.types.hubitat_component_gt import HubitatComponentGt
from sema.runtime.types.hubitat_poller_component_gt import HubitatPollerComponentGt
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt
from sema.runtime.types.web_server_component_gt import WebServerComponentGt


class GwHouse0Layout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.house0.layout/000"""

    g_nodes: list[GNodeGt] | None = None
    sh_nodes: list[SpaceheatNodeGt] | None = None
    data_channels: list[DataChannelGt] | None = None
    derived_channels: list[DerivedChannelGt] | None = None
    components: (
        list[
            ElectricMeterComponentGt
            | Ads111xBasedComponentGt
            | I2cMultichannelDtRelayComponentGt
            | DfrComponentGt
            | PicoFlowModuleComponentGt
            | PicoTankModuleComponentGt
            | SimPicoTankModuleComponentGt
            | HubitatComponentGt
            | HubitatPollerComponentGt
            | WebServerComponentGt
        ]
        | None
    ) = None
    device_types: (
        list[
            ElectricMeterDeviceTypeGt | Ads111xBasedDeviceTypeGt | Gw1ScadaDeviceTypeGt
        ]
        | None
    ) = None
    hydronic: dict[str, Any] | None = None
    type_name: Literal["gw.house0.layout"] = "gw.house0.layout"
    version: Literal["000"] = "000"
