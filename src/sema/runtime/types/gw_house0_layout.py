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
from sema.runtime.types.gw1_scada_device_type_gt import Gw1ScadaDeviceTypeGt
from sema.runtime.types.gw_house0_hydronic import GwHouse0Hydronic
from sema.runtime.types.hubitat_component_gt import HubitatComponentGt
from sema.runtime.types.hubitat_poller_component_gt import HubitatPollerComponentGt
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.old_versions.g_node_gt_004 import GNodeGt004
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

    g_nodes: list[GNodeGt004]
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
        Axiom 3: ZoneHeatCallChannel
        For each zone at 1-based index i in Hydronic.Zones, a DerivedChannel named
        "zone{i}-{Zone.Name}-heat-call" (lowercased) with Strategy "heat-call" SHALL exist, and a
        source DataChannel SHALL exist for that zone — either "zone{i}-{Zone.Name}-whitewire-pwr"
        (power-sourced, e.g. an eGauge whitewire reading) or "zone{i}-{Zone.Name}-opto-input"
        (opto-sourced, e.g. a gw108 reading the thermostat opto-coupler). The choice of source is
        per-zone.
        """
        if self.hydronic is None:
            return self
        derived_by_name = {d.name: d for d in (self.derived_channels or [])}
        data_names = {d.name for d in (self.data_channels or [])}
        for i, zone in enumerate(self.hydronic.zones or [], start=1):
            base = f"zone{i}-{zone.name}".lower()
            heat_call = f"{base}-heat-call"
            dc = derived_by_name.get(heat_call)
            if dc is None:
                raise ValueError(
                    f"Axiom 3 (ZoneHeatCallChannel) failed: missing DerivedChannel '{heat_call}'."
                )
            if dc.strategy != "heat-call":
                raise ValueError(
                    f"Axiom 3 (ZoneHeatCallChannel) failed: DerivedChannel '{heat_call}' must have "
                    f"Strategy 'heat-call', got '{dc.strategy}'."
                )
            whitewire = f"{base}-whitewire-pwr"
            opto = f"{base}-opto-input"
            if whitewire not in data_names and opto not in data_names:
                raise ValueError(
                    f"Axiom 3 (ZoneHeatCallChannel) failed: heat-call for zone {i} needs a source "
                    f"DataChannel — '{whitewire}' (power) or '{opto}' (opto)."
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

    @model_validator(mode="after")
    def check_axiom_5(self) -> Self:
        """
        Axiom 5: TransactivePowerChannel
        DerivedChannels SHALL contain exactly one channel whose Strategy is
        "transactive-power" — the metered transactive boundary, computed by the power-meter
        actor (not the derived-generator). Each name in that channel's InputChannelNames
        SHALL resolve to an existing DataChannel with TelemetryName "PowerW", and the
        AboutNode of each such DataChannel SHALL carry a NameplatePowerW. (The metered set
        is declared once here, replacing the former per-node InPowerMetering flag; the
        NameplatePowerW obligation folds in spaceheat.node.gt's retired
        InPowerMetering-requires-nameplate axiom.)
        """
        transactive = [
            d
            for d in (self.derived_channels or [])
            if d.strategy == "transactive-power"
        ]
        if len(transactive) != 1:
            raise ValueError(
                "Axiom 5 (TransactivePowerChannel) failed: expected exactly one "
                f"transactive-power DerivedChannel, found {len(transactive)}."
            )
        data_by_name = {d.name: d for d in (self.data_channels or [])}
        node_by_name = {n.name: n for n in (self.sh_nodes or [])}
        for name in transactive[0].input_channel_names:
            ch = data_by_name.get(name)
            if ch is None:
                raise ValueError(
                    f"Axiom 5 (TransactivePowerChannel) failed: input '{name}' is not a DataChannel."
                )
            if ch.telemetry_name != "PowerW":
                raise ValueError(
                    f"Axiom 5 (TransactivePowerChannel) failed: input '{name}' must be PowerW, "
                    f"got '{ch.telemetry_name}'."
                )
            node = node_by_name.get(ch.about_node_name)
            if node is None or node.nameplate_power_w is None:
                raise ValueError(
                    f"Axiom 5 (TransactivePowerChannel) failed: about-node "
                    f"'{ch.about_node_name}' of input '{name}' has no NameplatePowerW."
                )
        return self
