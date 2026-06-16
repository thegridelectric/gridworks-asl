from typing import Literal, Self
from pydantic import model_validator
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
from sema.runtime.types.gw_house0_hydronic import GwHouse0Hydronic
from sema.runtime.types.hubitat_component_gt import HubitatComponentGt
from sema.runtime.types.hubitat_poller_component_gt import HubitatPollerComponentGt
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.pico_btu_meter_component_gt import PicoBtuMeterComponentGt
from sema.runtime.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt
from sema.runtime.types.web_server_component_gt import WebServerComponentGt


class GwHouse0Layout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.house0.layout/000"""

    g_nodes: list[GNodeGt]
    sh_nodes: list[SpaceheatNodeGt]
    data_channels: list[DataChannelGt]
    derived_channels: list[DerivedChannelGt]
    components: list[
        ElectricMeterComponentGt
        | Ads111xBasedComponentGt
        | I2cMultichannelDtRelayComponentGt
        | DfrComponentGt
        | PicoBtuMeterComponentGt
        | PicoFlowModuleComponentGt
        | PicoTankModuleComponentGt
        | SimPicoTankModuleComponentGt
        | HubitatComponentGt
        | HubitatPollerComponentGt
        | WebServerComponentGt
    ]
    device_types: list[
        ElectricMeterDeviceTypeGt | Ads111xBasedDeviceTypeGt | Gw1ScadaDeviceTypeGt
    ]
    hydronic: GwHouse0Hydronic
    type_name: Literal["gw.house0.layout"] = "gw.house0.layout"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: GlobalIdUniqueness
        ShNode.ShNodeId, Component.ComponentId, DataChannel.Id, DerivedChannel.Id
        and GNode.GNodeId SHALL each be globally unique; no id value SHALL appear
        in more than one of these sets.
        """
        ids: list[str] = []
        ids += [n.sh_node_id for n in (self.sh_nodes or [])]
        ids += [c.component_id for c in (self.components or [])]
        ids += [d.id for d in (self.data_channels or [])]
        ids += [d.id for d in (self.derived_channels or [])]
        ids += [g.g_node_id for g in (self.g_nodes or [])]
        seen: set[str] = set()
        dupes: set[str] = set()
        for i in ids:
            if i in seen:
                dupes.add(i)
            seen.add(i)
        if dupes:
            raise ValueError(
                f"Axiom 1 (GlobalIdUniqueness) failed: duplicate ids {sorted(dupes)}"
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> Self:
        """
        Axiom 2: EssentialNodesExistence
        ShNodes SHALL include the primary-scada (s), ltn, leaf-ally (la),
        local-control (lc) and derived-generator nodes.
        """
        if not self.sh_nodes:
            return self
        required = {"s", "ltn", "la", "lc", "derived-generator"}
        names = {n.name for n in (self.sh_nodes or [])}
        missing = sorted(required - names)
        if missing:
            raise ValueError(
                f"Axiom 2 (EssentialNodesExistence) failed: missing essential nodes {missing}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> Self:
        """
        Axiom 3: ZoneWhitewirePwrChannel
        For each zone at 1-based index i in Hydronic.Zones, a channel named
        "zone{i}-{Zone.Name}-whitewire-pwr" (lowercased) SHALL exist in the union
        of DataChannels and DerivedChannels.
        """
        if self.hydronic is None:
            return self
        channels = {d.name for d in (self.data_channels or [])}
        channels |= {d.name for d in (self.derived_channels or [])}
        for i, zone in enumerate(self.hydronic.zones or [], start=1):
            name = f"zone{i}-{zone.name}".lower() + "-whitewire-pwr"
            if name not in channels:
                raise ValueError(
                    f"Axiom 3 (ZoneWhitewirePwrChannel) failed: missing channel '{name}'."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> Self:
        """
        Axiom 4: PrimaryFlowSourceChannelAgreement
        The "primary-flow" channel SHALL agree with Hydronic.PrimaryFlowSource. If
        PrimaryFlowSource is "Measured", a DataChannel named "primary-flow" SHALL exist
        and no DerivedChannel named "primary-flow" SHALL exist. If PrimaryFlowSource is
        "DerivedSiegSum", a DerivedChannel named "primary-flow" with Strategy "sum" SHALL
        exist and no DataChannel named "primary-flow" SHALL exist.
        """
        if self.hydronic is None:
            return self
        source = self.hydronic.primary_flow_source
        has_data = any(d.name == "primary-flow" for d in (self.data_channels or []))
        derived = [d for d in (self.derived_channels or []) if d.name == "primary-flow"]
        if source == "Measured":
            if not has_data:
                raise ValueError(
                    "Axiom 4 (PrimaryFlowSourceChannelAgreement) failed: Measured requires a "
                    "'primary-flow' DataChannel."
                )
            if derived:
                raise ValueError(
                    "Axiom 4 (PrimaryFlowSourceChannelAgreement) failed: Measured forbids a "
                    "'primary-flow' DerivedChannel."
                )
        elif source == "DerivedSiegSum":
            if not any(d.strategy == "sum" for d in derived):
                raise ValueError(
                    "Axiom 4 (PrimaryFlowSourceChannelAgreement) failed: DerivedSiegSum requires "
                    "a 'primary-flow' DerivedChannel with Strategy 'sum'."
                )
            if has_data:
                raise ValueError(
                    "Axiom 4 (PrimaryFlowSourceChannelAgreement) failed: DerivedSiegSum forbids a "
                    "'primary-flow' DataChannel."
                )
        return self
