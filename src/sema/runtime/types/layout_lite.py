from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import Gw1SeasonalStorageMode
from sema.runtime.enums import Gw1SystemMode
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.gw1_tank_temp_calibration_map import Gw1TankTempCalibrationMap
from sema.runtime.types.ha1_params import Ha1Params
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.old_versions.derived_channel_gt_001 import DerivedChannelGt001
from sema.runtime.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt


class LayoutLite(SemaType):
    """Sema: https://schemas.electricity.works/types/layout.lite/015"""

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
    sh_nodes: list[SpaceheatNodeGt]
    data_channels: list[DataChannelGt]
    derived_channels: list[DerivedChannelGt001]
    tank_module_components: list[
        PicoTankModuleComponentGt | SimPicoTankModuleComponentGt
    ]
    flow_module_components: list[PicoFlowModuleComponentGt]
    ha1_params: Ha1Params
    i2c_relay_component: I2cMultichannelDtRelayComponentGt | None = None
    t_map: Gw1TankTempCalibrationMap | None = None
    type_name: Literal["layout.lite"] = "layout.lite"
    version: Literal["015"] = "015"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "LayoutLite":
        """
        Axiom 1: DcNodeConsistency
        Every DataChannels.AboutNodeName and DataChannels.CapturedByNodeName SHALL reference
        an existing ShNodes.Name, and every captured-by node SHALL have an active
        ActorClass.
        """
        raise NotImplementedError("Axiom 1 validation is not implemented.")

    @model_validator(mode="after")
    def check_axiom_2(self) -> "LayoutLite":
        """
        Axiom 2: NodeHandleHierarchyConsistency
        Every ShNode with a dotted handle SHALL have its immediate boss present as another
        ShNode in the same payload.
        """
        raise NotImplementedError("Axiom 2 validation is not implemented.")

    @model_validator(mode="after")
    def check_axiom_3(self) -> "LayoutLite":
        """
        Axiom 3: CriticalZoneSubset
        CriticalZoneList SHALL be a subset of ZoneList.
        """
        raise NotImplementedError("Axiom 3 validation is not implemented.")

    @model_validator(mode="after")
    def check_axiom_4(self) -> "LayoutLite":
        """
        Axiom 4: DerivedNodeConsistency
        Every DerivedChannels.CreatedByNodeName SHALL reference an existing ShNodes.Name
        whose ActorClass is active.
        """
        raise NotImplementedError("Axiom 4 validation is not implemented.")
