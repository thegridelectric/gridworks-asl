from typing import Literal, Self
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.types.ads111x_based_component_gt import Ads111xBasedComponentGt
from sema.runtime.types.ads111x_based_device_type_gt import Ads111xBasedDeviceTypeGt
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.derived_channel_gt import DerivedChannelGt
from sema.runtime.types.device_component_gt import DeviceComponentGt
from sema.runtime.types.dfr_component_gt import DfrComponentGt
from sema.runtime.types.electric_meter_component_gt import ElectricMeterComponentGt
from sema.runtime.types.electric_meter_device_type_gt import ElectricMeterDeviceTypeGt
from sema.runtime.types.g_node_gt import GNodeGt
from sema.runtime.types.gpio_relay_component_gt import GpioRelayComponentGt
from sema.runtime.types.gpio_sensor_component_gt import GpioSensorComponentGt
from sema.runtime.types.gw1_scada_device_type_gt import Gw1ScadaDeviceTypeGt
from sema.runtime.types.gw_hydronic import GwHydronic
from sema.runtime.types.hp_device_type_gt import HpDeviceTypeGt
from sema.runtime.types.hubitat_component_gt import HubitatComponentGt
from sema.runtime.types.hubitat_poller_component_gt import HubitatPollerComponentGt
from sema.runtime.types.i2c_dac_output_component_gt import I2cDacOutputComponentGt
from sema.runtime.types.i2c_dac_writer_component_gt import I2cDacWriterComponentGt
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.i2c_relay_component_gt import I2cRelayComponentGt
from sema.runtime.types.i2c_thermistor_reader_component_gt import (
    I2cThermistorReaderComponentGt,
)
from sema.runtime.types.pico_btu_meter_component_gt import PicoBtuMeterComponentGt
from sema.runtime.types.pico_flow_module_component_gt import PicoFlowModuleComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.scada_board_component_gt import ScadaBoardComponentGt
from sema.runtime.types.sim_dac_writer_component_gt import SimDacWriterComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.sim_relay_component_gt import SimRelayComponentGt
from sema.runtime.types.sim_sensor_component_gt import SimSensorComponentGt
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
        | DeviceComponentGt
        | Ads111xBasedComponentGt
        | GpioRelayComponentGt
        | GpioSensorComponentGt
        | I2cDacOutputComponentGt
        | I2cDacWriterComponentGt
        | I2cMultichannelDtRelayComponentGt
        | I2cRelayComponentGt
        | I2cThermistorReaderComponentGt
        | DfrComponentGt
        | PicoBtuMeterComponentGt
        | PicoFlowModuleComponentGt
        | PicoTankModuleComponentGt
        | ScadaBoardComponentGt
        | SimDacWriterComponentGt
        | SimPicoTankModuleComponentGt
        | SimRelayComponentGt
        | SimSensorComponentGt
        | HubitatComponentGt
        | HubitatPollerComponentGt
        | WebServerComponentGt
    ]
    device_types: list[
        ElectricMeterDeviceTypeGt
        | Ads111xBasedDeviceTypeGt
        | Gw1ScadaDeviceTypeGt
        | HpDeviceTypeGt
    ]
    hydronic: GwHydronic
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
        Axiom 2: CoreShNodesExistenceAndActorClass
        ShNodes SHALL contain a node with each of the following Name / ActorClass pairs, and no
        additional ShNode with any of these Names SHALL exist:
          "s"                 → ActorClass "PrimaryScada"
          "s2"                → ActorClass "SecondaryScada"
          "power-meter"       → ActorClass "PowerMeter"
          "ltn"               → ActorClass "NoActor"
          "admin"             → ActorClass "NoActor"
          "auto"              → ActorClass "NoActor"
          "la"                → ActorClass "LeafAlly"
          "lc"                → ActorClass "LocalControl"
          "derived-generator" → ActorClass "DerivedGenerator"
        The effective handle (Handle if present, otherwise Name) of "admin" SHALL be "admin" and
        of "auto" SHALL be "auto".
        """
        if not self.sh_nodes:
            return self
        pairs = {
            "s": "PrimaryScada",
            "s2": "SecondaryScada",
            "power-meter": "PowerMeter",
            "ltn": "NoActor",
            "admin": "NoActor",
            "auto": "NoActor",
            "la": "LeafAlly",
            "lc": "LocalControl",
            "derived-generator": "DerivedGenerator",
        }
        nodes_by_name = {}
        for n in self.sh_nodes:
            nodes_by_name.setdefault(n.name, []).append(n)
        for name, actor_class in pairs.items():
            matches = nodes_by_name.get(name, [])
            if len(matches) != 1 or matches[0].actor_class != actor_class:
                raise ValueError(
                    f"Axiom 2 (CoreShNodesExistenceAndActorClass) failed: expected exactly one "
                    f"ShNode {name!r} with ActorClass {actor_class}."
                )
        for name, handle in (("admin", "admin"), ("auto", "auto")):
            node = nodes_by_name[name][0]
            effective = node.handle if node.handle is not None else node.name
            if effective != handle:
                raise ValueError(
                    f"Axiom 2 (CoreShNodesExistenceAndActorClass) failed: {name!r} effective "
                    f"handle is {effective!r}, expected {handle!r}."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> Self:
        """
        Axiom 3: CommandNodesExistenceAndActorClass
        ShNodes SHALL contain a node with each of the following Name / ActorClass pairs, and no
        additional ShNode with any of these Names SHALL exist:
          "n"           → ActorClass "NoActor"
          "backup"      → ActorClass "NoActor"
          "scada-blind" → ActorClass "NoActor"
          "pico-cycler" → ActorClass "PicoCycler"
          "hp-boss"     → ActorClass "HpBoss"
          "sieg-loop"   → ActorClass "SiegLoop"
        The effective handle of "n" SHALL be "auto.lc.n". (A gw.house0.layout plant has a
        siegenthaler loop; whether the loop is USED is operational, so sieg-loop and hp-boss are
        unconditional command nodes, dormant when unused.)
        """
        if not self.sh_nodes:
            return self
        pairs = {
            "n": "NoActor",
            "backup": "NoActor",
            "scada-blind": "NoActor",
            "pico-cycler": "PicoCycler",
            "hp-boss": "HpBoss",
            "sieg-loop": "SiegLoop",
        }
        nodes_by_name = {}
        for n in self.sh_nodes:
            nodes_by_name.setdefault(n.name, []).append(n)
        for name, actor_class in pairs.items():
            matches = nodes_by_name.get(name, [])
            if len(matches) != 1 or matches[0].actor_class != actor_class:
                raise ValueError(
                    f"Axiom 3 (CommandNodesExistenceAndActorClass) failed: expected exactly one "
                    f"ShNode {name!r} with ActorClass {actor_class}."
                )
        n_node = nodes_by_name["n"][0]
        effective = n_node.handle if n_node.handle is not None else n_node.name
        if effective != "auto.lc.n":
            raise ValueError(
                f"Axiom 3 (CommandNodesExistenceAndActorClass) failed: 'n' effective handle is "
                f"{effective!r}, expected 'auto.lc.n'."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> Self:
        """
        Axiom 4: ZoneHeatCallChannel
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
                    f"Axiom 4 (ZoneHeatCallChannel) failed: missing DerivedChannel '{heat_call}'."
                )
            if dc.strategy != "heat-call":
                raise ValueError(
                    f"Axiom 4 (ZoneHeatCallChannel) failed: DerivedChannel '{heat_call}' must have "
                    f"Strategy 'heat-call', got '{dc.strategy}'."
                )
            whitewire = f"{base}-whitewire-pwr"
            opto = f"{base}-opto-input"
            if whitewire not in data_names and opto not in data_names:
                raise ValueError(
                    f"Axiom 4 (ZoneHeatCallChannel) failed: heat-call for zone {i} needs a source "
                    f"DataChannel — '{whitewire}' (power) or '{opto}' (opto)."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_5(self) -> Self:
        """
        Axiom 5: PrimaryFlowSourceChannelAgreement
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
                    "Axiom 5 (PrimaryFlowSourceChannelAgreement) failed: Measured requires a "
                    "'primary-flow' DataChannel."
                )
            if derived:
                raise ValueError(
                    "Axiom 5 (PrimaryFlowSourceChannelAgreement) failed: Measured forbids a "
                    "'primary-flow' DerivedChannel."
                )
        elif source == "DerivedSiegSum":
            if not any(d.strategy == "sum" for d in derived):
                raise ValueError(
                    "Axiom 5 (PrimaryFlowSourceChannelAgreement) failed: DerivedSiegSum requires "
                    "a 'primary-flow' DerivedChannel with Strategy 'sum'."
                )
            if has_data:
                raise ValueError(
                    "Axiom 5 (PrimaryFlowSourceChannelAgreement) failed: DerivedSiegSum forbids a "
                    "'primary-flow' DataChannel."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_6(self) -> Self:
        """
        Axiom 6: TransactivePowerChannel
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
                "Axiom 6 (TransactivePowerChannel) failed: expected exactly one "
                f"transactive-power DerivedChannel, found {len(transactive)}."
            )
        data_by_name = {d.name: d for d in (self.data_channels or [])}
        node_by_name = {n.name: n for n in (self.sh_nodes or [])}
        for name in transactive[0].input_channel_names:
            ch = data_by_name.get(name)
            if ch is None:
                raise ValueError(
                    f"Axiom 6 (TransactivePowerChannel) failed: input '{name}' is not a DataChannel."
                )
            if ch.telemetry_name != "PowerW":
                raise ValueError(
                    f"Axiom 6 (TransactivePowerChannel) failed: input '{name}' must be PowerW, "
                    f"got '{ch.telemetry_name}'."
                )
            node = node_by_name.get(ch.about_node_name)
            if node is None or node.nameplate_power_w is None:
                raise ValueError(
                    f"Axiom 6 (TransactivePowerChannel) failed: about-node "
                    f"'{ch.about_node_name}' of input '{name}' has no NameplatePowerW."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_7(self) -> Self:
        """
        Axiom 7: RequiredSensing
        For each of the names "dist-flow" and "store-flow": a channel with that Name SHALL exist
        in DataChannels or in DerivedChannels. (Kind-agnostic by design — a name may migrate from
        raw DataChannel to same-name DerivedChannel without touching this contract. This list
        grows with the fixture surface.)
        """
        if not self.sh_nodes:
            return self
        names = {c.name for c in (self.data_channels or [])} | {
            c.name for c in (self.derived_channels or [])
        }
        missing = sorted({"dist-flow", "store-flow"} - names)
        if missing:
            raise ValueError(
                f"Axiom 7 (RequiredSensing) failed: missing channel(s) {missing}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_8(self) -> Self:
        """
        Axiom 8: SiegManifoldChannels
        For each of the names "sieg-cold", "sieg-flow", "sieg-flow-hz", "hp-loop-on-off-relay",
        and "hp-loop-keep-send-relay": a channel with that Name SHALL exist in DataChannels or in
        DerivedChannels — the siegenthaler loop cannot be controlled or observed without its
        sensing and valve-observation channels.
        """
        if not self.sh_nodes:
            return self
        names = {c.name for c in (self.data_channels or [])} | {
            c.name for c in (self.derived_channels or [])
        }
        required = {
            "sieg-cold",
            "sieg-flow",
            "sieg-flow-hz",
            "hp-loop-on-off-relay",
            "hp-loop-keep-send-relay",
        }
        missing = sorted(required - names)
        if missing:
            raise ValueError(
                f"Axiom 8 (SiegManifoldChannels) failed: missing channel(s) {missing}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_9(self) -> Self:
        """
        Axiom 9: SystemModelEnergyChannels
        DerivedChannels SHALL include channels named "usable-energy" and
        "required-energy". Each SHALL have CreatedByNodeName "derived-generator" and
        Strategy "system-model", and SHALL carry Parameters.EnergyModel.TypeName.
        Across the two channels those TypeNames SHALL be exactly
        gw0.usable.energy.layered and gw0.required.energy.layered — one of each, so
        the layout states which model produces each figure.
        """
        expected_models = {
            "gw0.usable.energy.layered",
            "gw0.required.energy.layered",
        }
        derived_by_name = {d.name: d for d in (self.derived_channels or [])}
        seen: set[str] = set()
        for name in ("usable-energy", "required-energy"):
            channel = derived_by_name.get(name)
            if channel is None:
                raise ValueError(
                    "Axiom 9 (SystemModelEnergyChannels) failed: DerivedChannel "
                    f"'{name}' is absent."
                )
            if channel.created_by_node_name != "derived-generator":
                raise ValueError(
                    f"Axiom 9 (SystemModelEnergyChannels) failed: '{name}' must be "
                    "created by 'derived-generator', got "
                    f"'{channel.created_by_node_name}'."
                )
            if channel.strategy != "system-model":
                raise ValueError(
                    f"Axiom 9 (SystemModelEnergyChannels) failed: '{name}' must use "
                    f"Strategy 'system-model', got '{channel.strategy}'."
                )
            model = (channel.parameters or {}).get("EnergyModel") or {}
            type_name = model.get("TypeName")
            if not type_name:
                raise ValueError(
                    f"Axiom 9 (SystemModelEnergyChannels) failed: '{name}' has no "
                    "Parameters.EnergyModel.TypeName."
                )
            if type_name not in expected_models:
                raise ValueError(
                    f"Axiom 9 (SystemModelEnergyChannels) failed: '{name}' names "
                    f"unsupported EnergyModel '{type_name}'."
                )
            seen.add(type_name)
        if seen != expected_models:
            raise ValueError(
                "Axiom 9 (SystemModelEnergyChannels) failed: the two channels must "
                f"name one of each model; got {sorted(seen)}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_10(self) -> Self:
        """
        Axiom 10: RequiredActuators
        a. ShNodes SHALL include nodes named "vdc-relay", "tstat-common-relay",
        "charge-discharge-relay", "hp-failsafe-relay", "hp-scada-ops-relay",
        "aquastat-ctrl-relay", "store-pump-relay", "primary-pump-failsafe-relay",
        "primary-pump-scada-ops-relay", "hp-loop-on-off-relay", and
        "hp-loop-keep-send-relay", each with ActorClass "Relay", and nodes named
        "dist-010v", "primary-010v", and "store-010v", each with ActorClass
        "ZeroTenOutputer". b. Hydronic.ZoneCallCircuits SHALL be non-empty, and each
        circuit's FailsafeRelayNode and OpsRelayNode SHALL name a ShNode in ShNodes with
        ActorClass "Relay".
        """
        actor_class_by_name = {
            n.name: str(n.actor_class) for n in (self.sh_nodes or [])
        }

        def class_or_raise(node_name: str, expected: str, role: str) -> None:
            actor_class = actor_class_by_name.get(node_name)
            if actor_class is None:
                raise ValueError(
                    f"Axiom 10 (RequiredActuators) failed: no ShNode named {node_name} ({role})."
                )
            if actor_class != expected:
                raise ValueError(
                    f"Axiom 10 (RequiredActuators) failed: {node_name} ({role}) has "
                    f"ActorClass {actor_class}, not {expected}."
                )

        for required in (
            "vdc-relay",
            "tstat-common-relay",
            "charge-discharge-relay",
            "hp-failsafe-relay",
            "hp-scada-ops-relay",
            "aquastat-ctrl-relay",
            "store-pump-relay",
            "primary-pump-failsafe-relay",
            "primary-pump-scada-ops-relay",
            "hp-loop-on-off-relay",
            "hp-loop-keep-send-relay",
        ):
            class_or_raise(required, "Relay", "plant relay")
        for required in ("dist-010v", "primary-010v", "store-010v"):
            class_or_raise(required, "ZeroTenOutputer", "0-10V output")
        circuits = self.hydronic.zone_call_circuits or []
        if not circuits:
            raise ValueError(
                "Axiom 10 (RequiredActuators) failed: Hydronic.ZoneCallCircuits is empty."
            )
        for circuit in circuits:
            class_or_raise(
                circuit.failsafe_relay_node, "Relay", "circuit failsafe relay"
            )
            class_or_raise(circuit.ops_relay_node, "Relay", "circuit ops relay")
        return self

    @model_validator(mode="after")
    def check_axiom_11(self) -> Self:
        """
        Axiom 11: RequiredHeatpumpEquipment
        ShNodes SHALL include nodes named "hp-odu" and "hp-idu" (a House0 home is a split
        system: the indoor unit does the refrigerant-to-water exchange), each with a
        ComponentId equal to the ComponentId of a Component in Components, and each with
        ActorClass "NoActor" unless it is the node Hydronic.HpCommandNodeName names, whose
        ActorClass CommandableHeatPump governs.
        """
        component_ids = {c.component_id for c in (self.components or [])}
        nodes = {n.name: n for n in (self.sh_nodes or [])}
        for name in ("hp-odu", "hp-idu"):
            node = nodes.get(name)
            if node is None:
                raise ValueError(
                    f"Axiom 11 (RequiredHeatpumpEquipment) failed: no ShNode named {name!r}."
                )
            if node.component_id is None or node.component_id not in component_ids:
                raise ValueError(
                    f"Axiom 11 (RequiredHeatpumpEquipment) failed: {name!r} has no "
                    "ComponentId resolving to a Component."
                )
            if name == self.hydronic.hp_command_node_name:
                continue  # ActorClass governed by CommandableHeatPump
            if str(node.actor_class) != "NoActor":
                raise ValueError(
                    f"Axiom 11 (RequiredHeatpumpEquipment) failed: {name!r} has ActorClass "
                    f"{node.actor_class}, expected NoActor."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_12(self) -> Self:
        """
        Axiom 12: CommandableHeatPump
        a. If Hydronic.HpCommandNodeName is present, it SHALL equal the Name of a ShNode in
        ShNodes named "hp-odu", "hp-idu" or "hp-ctrl-box", whose ComponentId equals the
        ComponentId of a Component in Components, whose ActorClass is "HpTwin", and whose
        effective handle (Handle if present, otherwise Name) has the effective handle of the
        ShNode named "hp-boss" as its parent prefix.
        b. Every ShNode with ActorClass "HpTwin" SHALL be the node Hydronic.HpCommandNodeName
        names; when HpCommandNodeName is absent no ShNode SHALL have ActorClass "HpTwin".
        """
        declared = self.hydronic.hp_command_node_name
        nodes = {n.name: n for n in (self.sh_nodes or [])}
        if declared is not None:
            node = nodes.get(declared)
            if node is None or declared not in ("hp-odu", "hp-idu", "hp-ctrl-box"):
                raise ValueError(
                    f"Axiom 12 (CommandableHeatPump) failed: HpCommandNodeName {declared!r} "
                    "is not an ShNode named hp-odu, hp-idu or hp-ctrl-box."
                )
            component_ids = {c.component_id for c in (self.components or [])}
            if node.component_id is None or node.component_id not in component_ids:
                raise ValueError(
                    f"Axiom 12 (CommandableHeatPump) failed: {declared!r} has no "
                    "ComponentId resolving to a Component."
                )
            if str(node.actor_class) != "HpTwin":
                raise ValueError(
                    f"Axiom 12 (CommandableHeatPump) failed: {declared!r} has ActorClass "
                    f"{node.actor_class}, expected HpTwin."
                )
            hp_boss = nodes.get("hp-boss")
            boss_handle = (
                (hp_boss.handle or hp_boss.name) if hp_boss is not None else None
            )
            handle = node.handle or node.name
            if (
                boss_handle is None
                or handle.rsplit(".", 1)[0] != boss_handle
                or "." not in handle
            ):
                raise ValueError(
                    f"Axiom 12 (CommandableHeatPump) failed: {declared!r} handle {handle!r} "
                    f"is not directly under hp-boss ({boss_handle!r})."
                )
        for n in nodes.values():
            if str(n.actor_class) == "HpTwin" and n.name != declared:
                raise ValueError(
                    f"Axiom 12 (CommandableHeatPump) failed: {n.name!r} has ActorClass HpTwin "
                    f"but HpCommandNodeName is {declared!r}."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_13(self) -> Self:
        """
        Axiom 13: PrefixClosedHandles
        Let the effective handle of an ShNode be its Handle if present, otherwise
        its Name. The set of effective handles SHALL be prefix-closed: for every ShNode
        in ShNodes, each dot-separated prefix of its effective handle SHALL also be the
        effective handle of some ShNode in ShNodes.
        """
        effective = {
            node.handle if node.handle is not None else node.name
            for node in self.sh_nodes
        }
        for value in effective:
            segments = value.split(".")
            for n in range(1, len(segments)):
                prefix = ".".join(segments[:n])
                if prefix not in effective:
                    raise ValueError(
                        f"Axiom 13 failed: effective handle {value!r} has "
                        f"prefix {prefix!r} that is not the effective handle "
                        "of any ShNode."
                    )
        return self

    @model_validator(mode="after")
    def check_axiom_14(self) -> Self:
        """
        Axiom 14: ActuatorLeaves
        Let the effective handle of an ShNode be its Handle if present, otherwise
        its Name. A leaf is an ShNode whose effective handle contains a dot and is
        the parent prefix of no other effective handle. An actuator is an ShNode
        whose ActorClass is "Relay", "ZeroTenOutputer" or "HpTwin". A command node
        is an ShNode whose ActorClass is "LocalControl", "LeafAlly", "PicoCycler",
        "HpBoss" or "SiegLoop", or whose ActorClass is "NoActor" and whose
        effective handle's parent prefix is the effective handle of an ShNode with
        ActorClass "LocalControl".
        a. Every actuator SHALL have a dotted effective handle and SHALL be a leaf.
        b. Every leaf SHALL be an actuator or a command node.
        """
        actuator_classes = {"Relay", "ZeroTenOutputer", "HpTwin"}
        command_classes = {
            "LocalControl",
            "LeafAlly",
            "PicoCycler",
            "HpBoss",
            "SiegLoop",
        }
        by_handle = {
            (node.handle if node.handle is not None else node.name): node
            for node in self.sh_nodes
        }
        handles = set(by_handle)
        lc_handles = {
            h for h, n in by_handle.items() if str(n.actor_class) == "LocalControl"
        }

        def is_leaf(handle: str) -> bool:
            return "." in handle and not any(
                other.startswith(handle + ".") for other in handles
            )

        for handle, node in by_handle.items():
            actor_class = str(node.actor_class)
            if actor_class in actuator_classes and not is_leaf(handle):
                raise ValueError(
                    f"Axiom 14 (ActuatorLeaves) failed: actuator {node.name!r} with "
                    f"handle {handle!r} is not a dotted-handle leaf."
                )
            if is_leaf(handle):
                parent = handle.rsplit(".", 1)[0]
                is_command = actor_class in command_classes or (
                    actor_class == "NoActor" and parent in lc_handles
                )
                if actor_class not in actuator_classes and not is_command:
                    raise ValueError(
                        f"Axiom 14 (ActuatorLeaves) failed: leaf {node.name!r} with "
                        f"handle {handle!r} (ActorClass {actor_class}) is neither an "
                        "actuator nor a command node."
                    )
        return self
