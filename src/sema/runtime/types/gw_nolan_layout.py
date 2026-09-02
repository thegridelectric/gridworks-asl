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
from sema.runtime.types.i2c_dac_writer_component_gt import I2cDacWriterComponentGt
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
from sema.runtime.types.sim_dac_writer_component_gt import SimDacWriterComponentGt
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
        | I2cDacWriterComponentGt
        | I2cMultichannelDtRelayComponentGt
        | I2cRelayComponentGt
        | I2cThermistorReaderComponentGt
        | ScadaBoardComponentGt
        | PicoBtuMeterComponentGt
        | PicoTankModuleComponentGt
        | SimDacWriterComponentGt
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
        ActorClass "Relay".
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
        return self

    @model_validator(mode="after")
    def check_axiom_6(self) -> "GwNolanLayout":
        """
        Axiom 6: RequiredHeatpumpEquipment
        ShNodes SHALL include nodes named "hp-odu" and "hp-ctrl-box" (a Nolan home is a
        monobloc), each with a ComponentId equal to the ComponentId of a Component in
        Components, and each with ActorClass "NoActor".
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
