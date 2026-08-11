from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.types.ads111x_based_device_type_gt import Ads111xBasedDeviceTypeGt
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.derived_channel_gt import DerivedChannelGt
from sema.runtime.types.electric_meter_component_gt import ElectricMeterComponentGt
from sema.runtime.types.electric_meter_device_type_gt import ElectricMeterDeviceTypeGt
from sema.runtime.types.g_node_gt import GNodeGt
from sema.runtime.types.gpio_relay_component_gt import GpioRelayComponentGt
from sema.runtime.types.gpio_sensor_component_gt import GpioSensorComponentGt
from sema.runtime.types.gw1_scada_device_type_gt import Gw1ScadaDeviceTypeGt
from sema.runtime.types.gw_hydronic import GwHydronic
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
from sema.runtime.types.sim_pico_tank_module_component_gt import (
    SimPicoTankModuleComponentGt,
)
from sema.runtime.types.spaceheat_node_gt import SpaceheatNodeGt
from sema.runtime.types.web_server_component_gt import WebServerComponentGt


class GwNolanLayout(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.nolan.layout/000"""

    g_nodes: list[GNodeGt]
    sh_nodes: list[SpaceheatNodeGt]
    data_channels: list[DataChannelGt]
    derived_channels: list[DerivedChannelGt]
    components: list[
        ElectricMeterComponentGt
        | GpioSensorComponentGt
        | GpioRelayComponentGt
        | I2cDacWriterComponentGt
        | I2cMultichannelDtRelayComponentGt
        | I2cRelayComponentGt
        | I2cThermistorReaderComponentGt
        | ScadaBoardComponentGt
        | PicoBtuMeterComponentGt
        | PicoTankModuleComponentGt
        | SimPicoTankModuleComponentGt
        | WebServerComponentGt
    ]
    device_types: list[
        ElectricMeterDeviceTypeGt | Ads111xBasedDeviceTypeGt | Gw1ScadaDeviceTypeGt
    ]
    hydronic: GwHydronic
    type_name: Literal["gw.nolan.layout"] = "gw.nolan.layout"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwNolanLayout":
        """
        Axiom 1: TransactivePowerChannel
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
