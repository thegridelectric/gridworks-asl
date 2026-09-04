from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.types.ads111x_based_device_type_gt import Ads111xBasedDeviceTypeGt
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.derived_channel_gt import DerivedChannelGt
from sema.runtime.types.device_component_gt import DeviceComponentGt
from sema.runtime.types.electric_meter_component_gt import ElectricMeterComponentGt
from sema.runtime.types.electric_meter_device_type_gt import ElectricMeterDeviceTypeGt
from sema.runtime.types.g_node_gt import GNodeGt
from sema.runtime.types.gpio_relay_component_gt import GpioRelayComponentGt
from sema.runtime.types.gpio_sensor_component_gt import GpioSensorComponentGt
from sema.runtime.types.gw1_scada_device_type_gt import Gw1ScadaDeviceTypeGt
from sema.runtime.types.gw_hydronic import GwHydronic
from sema.runtime.types.hp_control_box_device_type_gt import HpControlBoxDeviceTypeGt
from sema.runtime.types.hp_device_type_gt import HpDeviceTypeGt
from sema.runtime.types.i2c_dac_output_component_gt import I2cDacOutputComponentGt
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)
from sema.runtime.types.i2c_relay_component_gt import I2cRelayComponentGt
from sema.runtime.types.i2c_thermistor_reader_component_gt import (
    I2cThermistorReaderComponentGt,
)
from sema.runtime.types.pico_btu_meter_component_gt import PicoBtuMeterComponentGt
from sema.runtime.types.pico_tank_module_component_gt import PicoTankModuleComponentGt
from sema.runtime.types.scada_board_component_gt import ScadaBoardComponentGt
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.sim_relay_component_gt import SimRelayComponentGt
from sema.runtime.types.sim_sensor_component_gt import SimSensorComponentGt
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt
from sema.runtime.types.web_server_component_gt import WebServerComponentGt


class GwNolanLayout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.nolan.layout/000"""

    g_nodes: list[GNodeGt]
    sh_nodes: list[SpaceheatNodeGt]
    data_channels: list[DataChannelGt]
    derived_channels: list[DerivedChannelGt]
    components: list[
        DeviceComponentGt
        | ElectricMeterComponentGt
        | GpioSensorComponentGt
        | GpioRelayComponentGt
        | I2cDacOutputComponentGt
        | I2cMultichannelDtRelayComponentGt
        | I2cRelayComponentGt
        | I2cThermistorReaderComponentGt
        | ScadaBoardComponentGt
        | PicoBtuMeterComponentGt
        | PicoTankModuleComponentGt
        | SimPicoTankModuleComponentGt
        | SimRelayComponentGt
        | SimSensorComponentGt
        | WebServerComponentGt
    ]
    device_types: list[
        ElectricMeterDeviceTypeGt
        | Ads111xBasedDeviceTypeGt
        | Gw1ScadaDeviceTypeGt
        | HpDeviceTypeGt
        | HpControlBoxDeviceTypeGt
    ]
    hydronic: GwHydronic
    type_name: Literal["gw.nolan.layout"] = "gw.nolan.layout"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwNolanLayout":
        """
        Axiom 1: TransactivePowerChannel
        DerivedChannels SHALL contain exactly one channel whose Strategy is
        "transactive-power" — the metered transactive boundary, computed by the
        power-meter actor (not the derived-generator). Each name in that channel's
        InputChannelNames SHALL resolve to an existing DataChannel with TelemetryName
        "PowerW", and the AboutNode of each such DataChannel SHALL carry a
        NameplatePowerW. (The metered set is declared once here, replacing the former
        per-node InPowerMetering flag; the NameplatePowerW obligation folds in
        spaceheat.node.gt's retired InPowerMetering-requires-nameplate axiom.)
        """
        transactive = [
            d
            for d in (self.derived_channels or [])
            if d.strategy == "transactive-power"
        ]
        if len(transactive) != 1:
            raise ValueError(
                "Axiom 1 (TransactivePowerChannel) failed: expected exactly one "
                f"transactive-power DerivedChannel, found {len(transactive)}."
            )
        data_by_name = {d.name: d for d in (self.data_channels or [])}
        node_by_name = {n.name: n for n in (self.sh_nodes or [])}
        for name in transactive[0].input_channel_names:
            ch = data_by_name.get(name)
            if ch is None:
                raise ValueError(
                    f"Axiom 1 (TransactivePowerChannel) failed: input '{name}' is not a DataChannel."
                )
            if ch.telemetry_name != "PowerW":
                raise ValueError(
                    f"Axiom 1 (TransactivePowerChannel) failed: input '{name}' must be PowerW, "
                    f"got '{ch.telemetry_name}'."
                )
            node = node_by_name.get(ch.about_node_name)
            if node is None or node.nameplate_power_w is None:
                raise ValueError(
                    f"Axiom 1 (TransactivePowerChannel) failed: about-node "
                    f"'{ch.about_node_name}' of input '{name}' has no NameplatePowerW."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwNolanLayout":
        """
        Axiom 2: BoardResolution
        For every board-resident component in Components (gpio.sensor.component.gt,
        gpio.relay.component.gt, i2c.thermistor.reader.component.gt): its
        BoardComponentId SHALL equal the ComponentId of a scada.board.component.gt in
        Components; that board component's DeviceType SHALL match the DeviceType of a
        gw1.scada.device.type.gt record in DeviceTypes; and the component's board name
        (GpioName against NativeGpioInputs for sensors, GpioName against
        NativeGpioOutputs for relays, AdcName against the ThermistorAdcs Names for
        thermistor readers) SHALL match a Name in that record.
        """
        boards = {
            c.component_id: c
            for c in (self.components or [])
            if c.type_name == "scada.board.component.gt"
        }
        records = {
            r.device_type: r
            for r in (self.device_types or [])
            if r.type_name == "gw1.scada.device.type.gt"
        }
        kinds = {
            "gpio.sensor.component.gt": ("gpio_name", "native_gpio_inputs"),
            "gpio.relay.component.gt": ("gpio_name", "native_gpio_outputs"),
            "i2c.thermistor.reader.component.gt": ("adc_name", "thermistor_adcs"),
        }
        for c in self.components or []:
            kind = kinds.get(c.type_name)
            if kind is None:
                continue
            attr, list_name = kind
            board = boards.get(c.board_component_id)
            if board is None:
                raise ValueError(
                    "Axiom 2 (BoardResolution) failed: BoardComponentId "
                    f"'{c.board_component_id}' of component '{c.component_id}' does "
                    "not resolve to a scada.board.component.gt."
                )
            record = records.get(board.device_type)
            if record is None:
                raise ValueError(
                    "Axiom 2 (BoardResolution) failed: board DeviceType "
                    f"'{board.device_type}' has no gw1.scada.device.type.gt record."
                )
            wanted = getattr(c, attr)
            entries = getattr(record, list_name) or []
            names = {e.name for e in entries}
            if wanted not in names:
                raise ValueError(
                    "Axiom 2 (BoardResolution) failed: name "
                    f"'{wanted}' of component '{c.component_id}' is not in the "
                    f"board record's {list_name}."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "GwNolanLayout":
        """
        Axiom 3: CoreShNodesExistenceAndActorClass
        ShNodes SHALL contain a node with each of the following Name / ActorClass pairs,
        and no additional ShNode with any of these Names SHALL exist: "s" → ActorClass
        "PrimaryScada" "s2" → ActorClass "SecondaryScada" "power-meter" → ActorClass
        "PowerMeter" "ltn" → ActorClass "NoActor" "admin" → ActorClass "NoActor" "auto"
        → ActorClass "NoActor" "la" → ActorClass "LeafAlly" "lc" → ActorClass
        "LocalControl" "derived-generator" → ActorClass "DerivedGenerator" The effective
        handle (Handle if present, otherwise Name) of "admin" SHALL be "admin" and of
        "auto" SHALL be "auto".
        """
        pairs = (
            ("s", "PrimaryScada"),
            ("s2", "SecondaryScada"),
            ("power-meter", "PowerMeter"),
            ("ltn", "NoActor"),
            ("admin", "NoActor"),
            ("auto", "NoActor"),
            ("la", "LeafAlly"),
            ("lc", "LocalControl"),
            ("derived-generator", "DerivedGenerator"),
        )
        nodes = [n for n in (self.sh_nodes or [])]
        for name, actor_class in pairs:
            matches = [n for n in nodes if n.name == name]
            if len(matches) != 1:
                raise ValueError(
                    "Axiom 3 (CoreShNodesExistenceAndActorClass) failed: expected exactly "
                    f"one ShNode named {name!r}, found {len(matches)}."
                )
            if str(matches[0].actor_class) != actor_class:
                raise ValueError(
                    "Axiom 3 (CoreShNodesExistenceAndActorClass) failed: ShNode "
                    f"{name!r} has ActorClass {matches[0].actor_class}, expected {actor_class}."
                )
        for name, handle in (("admin", "admin"), ("auto", "auto")):
            node = next(n for n in nodes if n.name == name)
            effective = node.handle if node.handle is not None else node.name
            if effective != handle:
                raise ValueError(
                    "Axiom 3 (CoreShNodesExistenceAndActorClass) failed: "
                    f"{name!r} effective handle is {effective!r}, expected {handle!r}."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "GwNolanLayout":
        """
        Axiom 4: CommandNodesExistenceAndActorClass
        ShNodes SHALL contain a node with each of the following Name / ActorClass pairs,
        and no additional ShNode with any of these Names SHALL exist: "n" → ActorClass
        "NoActor" "pico-cycler" → ActorClass "PicoCycler" "hp-boss" → ActorClass
        "HpBoss" The effective handle of "n" SHALL be "auto.lc.n". (hp-boss is a command
        node in every layout: hp-scada-ops-relay reports to it in all states, dormant
        when no heat pump is commandable.)
        """
        pairs = (("n", "NoActor"), ("pico-cycler", "PicoCycler"), ("hp-boss", "HpBoss"))
        nodes = [n for n in (self.sh_nodes or [])]
        for name, actor_class in pairs:
            matches = [n for n in nodes if n.name == name]
            if len(matches) != 1:
                raise ValueError(
                    "Axiom 4 (CommandNodesExistenceAndActorClass) failed: expected exactly "
                    f"one ShNode named {name!r}, found {len(matches)}."
                )
            if str(matches[0].actor_class) != actor_class:
                raise ValueError(
                    "Axiom 4 (CommandNodesExistenceAndActorClass) failed: ShNode "
                    f"{name!r} has ActorClass {matches[0].actor_class}, expected {actor_class}."
                )
        node = next(n for n in nodes if n.name == "n")
        effective = node.handle if node.handle is not None else node.name
        if effective != "auto.lc.n":
            raise ValueError(
                "Axiom 4 (CommandNodesExistenceAndActorClass) failed: 'n' effective "
                f"handle is {effective!r}, expected 'auto.lc.n'."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_5(self) -> "GwNolanLayout":
        """
        Axiom 5: RequiredActuators
        a. ShNodes SHALL include nodes named "iso-valve-relay", "secondary-pump-relay",
        "hp-scada-ops-relay", "charge-valve-relay", "store-pump-relay",
        "buffer-top-elt-relay", "buffer-bottom-elt-relay", "tank1-top-elt-relay", and
        "tank1-bottom-elt-relay", each with ActorClass "Relay". b.
        Hydronic.ZoneCallCircuits SHALL be non-empty, and each circuit's
        FailsafeRelayNode and OpsRelayNode SHALL name a ShNode in ShNodes with
        ActorClass "Relay". c. ShNodes SHALL include a node named "secondary-010v" with
        ActorClass "ZeroTenOutputer" and a ComponentId equal to the ComponentId of an
        i2c.dac.output.component.gt in Components.
        """
        actor_class_by_name = {
            n.name: str(n.actor_class) for n in (self.sh_nodes or [])
        }

        def relay_or_raise(node_name: str, role: str) -> None:
            actor_class = actor_class_by_name.get(node_name)
            if actor_class is None:
                raise ValueError(
                    f"Axiom 5 (RequiredActuators) failed: no ShNode named {node_name} ({role})."
                )
            if actor_class != "Relay":
                raise ValueError(
                    f"Axiom 5 (RequiredActuators) failed: {node_name} ({role}) has "
                    f"ActorClass {actor_class}, not Relay."
                )

        for required in (
            "iso-valve-relay",
            "secondary-pump-relay",
            "hp-scada-ops-relay",
            "charge-valve-relay",
            "store-pump-relay",
            "buffer-top-elt-relay",
            "buffer-bottom-elt-relay",
            "tank1-top-elt-relay",
            "tank1-bottom-elt-relay",
        ):
            relay_or_raise(required, "plant relay")
        circuits = self.hydronic.zone_call_circuits or []
        if not circuits:
            raise ValueError(
                "Axiom 5 (RequiredActuators) failed: Hydronic.ZoneCallCircuits is empty."
            )
        for circuit in circuits:
            relay_or_raise(circuit.failsafe_relay_node, "circuit failsafe relay")
            relay_or_raise(circuit.ops_relay_node, "circuit ops relay")
        output_node = next(
            (n for n in (self.sh_nodes or []) if n.name == "secondary-010v"), None
        )
        if output_node is None:
            raise ValueError(
                "Axiom 5 (RequiredActuators) failed: no ShNode named secondary-010v."
            )
        if str(output_node.actor_class) != "ZeroTenOutputer":
            raise ValueError(
                "Axiom 5 (RequiredActuators) failed: secondary-010v has ActorClass "
                f"{output_node.actor_class}, not ZeroTenOutputer."
            )
        dac_output_ids = {
            c.component_id
            for c in (self.components or [])
            if isinstance(c, I2cDacOutputComponentGt)
        }
        if output_node.component_id not in dac_output_ids:
            raise ValueError(
                "Axiom 5 (RequiredActuators) failed: secondary-010v ComponentId "
                f"{output_node.component_id} is not an i2c.dac.output.component.gt in Components."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_6(self) -> "GwNolanLayout":
        """
        Axiom 6: RequiredHeatpumpEquipment
        ShNodes SHALL include nodes named "hp-odu" and "hp-ctrl-box" (a Nolan home is a
        monobloc), each with a ComponentId equal to the ComponentId of a Component in
        Components, and each with ActorClass "NoActor" unless it is the node
        Hydronic.HpCommandNodeName names, whose ActorClass CommandableHeatPump governs.
        """
        component_ids = {c.component_id for c in (self.components or [])}
        nodes = {n.name: n for n in (self.sh_nodes or [])}
        for name in ("hp-odu", "hp-ctrl-box"):
            node = nodes.get(name)
            if node is None:
                raise ValueError(
                    f"Axiom 6 (RequiredHeatpumpEquipment) failed: no ShNode named {name!r}."
                )
            if node.component_id is None or node.component_id not in component_ids:
                raise ValueError(
                    f"Axiom 6 (RequiredHeatpumpEquipment) failed: {name!r} has no "
                    "ComponentId resolving to a Component."
                )
            if name == self.hydronic.hp_command_node_name:
                continue  # ActorClass governed by CommandableHeatPump
            if str(node.actor_class) != "NoActor":
                raise ValueError(
                    f"Axiom 6 (RequiredHeatpumpEquipment) failed: {name!r} has ActorClass "
                    f"{node.actor_class}, expected NoActor."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_7(self) -> "GwNolanLayout":
        """
        Axiom 7: ComponentBinding
        Every Component in Components SHALL have its ComponentId referenced by exactly
        one ShNode in ShNodes. The node's Name is the component's identity within the
        house; the ComponentId is the replaceable instance under it (a swapped part
        keeps the name and gets a fresh id).
        """
        refs: dict[str, int] = {}
        for n in self.sh_nodes or []:
            if n.component_id is not None:
                refs[n.component_id] = refs.get(n.component_id, 0) + 1
        violations = {
            c.component_id: refs.get(c.component_id, 0)
            for c in (self.components or [])
            if refs.get(c.component_id, 0) != 1
        }
        if violations:
            raise ValueError(
                "Axiom 7 (ComponentBinding) failed: components not referenced by exactly "
                f"one ShNode (id: reference count) {violations}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_8(self) -> "GwNolanLayout":
        """
        Axiom 8: RequiredSensing
        For each of the names "hp-lwt", "hp-ewt", "dist-swt", "dist-rwt",
        "store-hot-pipe", "store-cold-pipe", "secondary-lwt", "secondary-ewt",
        "dist-flow", "primary-flow", "store-flow", "secondary-flow",
        "buffer-depth1-device", "buffer-depth2-device", "buffer-depth3-device",
        "tank1-depth1-device", "tank1-depth2-device", "tank1-depth3-device",
        "hp-odu-pwr", "hp-ctrl-box-pwr", "buffer-top-elt-pwr", "buffer-bottom-elt-pwr",
        "tank1-top-elt-pwr", and "tank1-bottom-elt-pwr": a channel with that Name SHALL
        exist in DataChannels or in DerivedChannels. (Kind-agnostic by design: a name
        may migrate from raw DataChannel to same-name DerivedChannel — as tank
        temperatures did — without touching this contract.)
        """
        channel_names = {c.name for c in (self.data_channels or [])} | {
            c.name for c in (self.derived_channels or [])
        }
        missing = [
            name
            for name in (
                "hp-lwt",
                "hp-ewt",
                "dist-swt",
                "dist-rwt",
                "store-hot-pipe",
                "store-cold-pipe",
                "secondary-lwt",
                "secondary-ewt",
                "dist-flow",
                "primary-flow",
                "store-flow",
                "secondary-flow",
                "buffer-depth1-device",
                "buffer-depth2-device",
                "buffer-depth3-device",
                "tank1-depth1-device",
                "tank1-depth2-device",
                "tank1-depth3-device",
                "hp-odu-pwr",
                "hp-ctrl-box-pwr",
                "buffer-top-elt-pwr",
                "buffer-bottom-elt-pwr",
                "tank1-top-elt-pwr",
                "tank1-bottom-elt-pwr",
            )
            if name not in channel_names
        ]
        if missing:
            raise ValueError(
                f"Axiom 8 (RequiredSensing) failed: missing channels {missing}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_9(self) -> "GwNolanLayout":
        """
        Axiom 9: SingleStoreTank
        Hydronic.TotalStoreTanks SHALL equal 1 — the Nolan plant carries exactly one
        store tank.
        """
        if self.hydronic.total_store_tanks != 1:
            raise ValueError(
                "Axiom 9 (SingleStoreTank) failed: TotalStoreTanks is "
                f"{self.hydronic.total_store_tanks}, expected 1."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_10(self) -> "GwNolanLayout":
        """
        Axiom 10: CommandableHeatPump
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
                    f"Axiom 10 (CommandableHeatPump) failed: HpCommandNodeName {declared!r} "
                    "is not an ShNode named hp-odu, hp-idu or hp-ctrl-box."
                )
            component_ids = {c.component_id for c in (self.components or [])}
            if node.component_id is None or node.component_id not in component_ids:
                raise ValueError(
                    f"Axiom 10 (CommandableHeatPump) failed: {declared!r} has no "
                    "ComponentId resolving to a Component."
                )
            if str(node.actor_class) != "HpTwin":
                raise ValueError(
                    f"Axiom 10 (CommandableHeatPump) failed: {declared!r} has ActorClass "
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
                    f"Axiom 10 (CommandableHeatPump) failed: {declared!r} handle {handle!r} "
                    f"is not directly under hp-boss ({boss_handle!r})."
                )
        for n in nodes.values():
            if str(n.actor_class) == "HpTwin" and n.name != declared:
                raise ValueError(
                    f"Axiom 10 (CommandableHeatPump) failed: {n.name!r} has ActorClass HpTwin "
                    f"but HpCommandNodeName is {declared!r}."
                )
        return self

    @model_validator(mode="after")
    def check_axiom_11(self) -> "GwNolanLayout":
        """
        Axiom 11: PrefixClosedHandles
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
                        f"Axiom 11 failed: effective handle {value!r} has "
                        f"prefix {prefix!r} that is not the effective handle "
                        "of any ShNode."
                    )
        return self

    @model_validator(mode="after")
    def check_axiom_12(self) -> "GwNolanLayout":
        """
        Axiom 12: ActuatorLeaves
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
                    f"Axiom 12 (ActuatorLeaves) failed: actuator {node.name!r} with "
                    f"handle {handle!r} is not a dotted-handle leaf."
                )
            if is_leaf(handle):
                parent = handle.rsplit(".", 1)[0]
                is_command = actor_class in command_classes or (
                    actor_class == "NoActor" and parent in lc_handles
                )
                if actor_class not in actuator_classes and not is_command:
                    raise ValueError(
                        f"Axiom 12 (ActuatorLeaves) failed: leaf {node.name!r} with "
                        f"handle {handle!r} (ActorClass {actor_class}) is neither an "
                        "actuator nor a command node."
                    )
        return self
