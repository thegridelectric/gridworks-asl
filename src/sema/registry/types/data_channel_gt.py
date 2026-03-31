import uuid
from typing import Literal

from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.enums.gw1_quantity import Gw1Quantity
from sema.registry.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.registry.property_format import LeftRightDot, SpaceheatName, UTCSeconds, UUID4Str


_TELEMETRY_QUANTITY_PROJECTION = {
    SpaceheatTelemetryName.Unknown: Gw1Quantity.Unknown,
    SpaceheatTelemetryName.PowerW: Gw1Quantity.Power,
    SpaceheatTelemetryName.RelayState: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.WaterTempCTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.WaterTempFTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.GpmTimes100: Gw1Quantity.FlowRate,
    SpaceheatTelemetryName.CurrentRmsMicroAmps: Gw1Quantity.Current,
    SpaceheatTelemetryName.GallonsTimes100: Gw1Quantity.Volume,
    SpaceheatTelemetryName.VoltageRmsMilliVolts: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.MilliWattHours: Gw1Quantity.Energy,
    SpaceheatTelemetryName.MicroHz: Gw1Quantity.Frequency,
    SpaceheatTelemetryName.AirTempCTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.AirTempFTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.ThermostatState: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.MicroVolts: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.VoltsTimesTen: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.WattHours: Gw1Quantity.Energy,
    SpaceheatTelemetryName.StorageLayer: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.PercentKeep: Gw1Quantity.Percent,
    SpaceheatTelemetryName.CelsiusTimes100: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.VoltsTimes100: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.HzTimes100: Gw1Quantity.Frequency,
    SpaceheatTelemetryName.BinaryState: Gw1Quantity.Unitless,
}


class DataChannelGt(SemaType):
    """Sema: https://schemas.electricity.works/types/data.channel.gt/002"""

    name: SpaceheatName
    display_name: str
    about_node_name: SpaceheatName
    captured_by_node_name: SpaceheatName
    telemetry_name: SpaceheatTelemetryName
    quantity: Gw1Quantity
    terminal_asset_alias: LeftRightDot
    in_power_metering: bool | None = None
    start_s: UTCSeconds | None = None
    id: UUID4Str
    type_name: Literal["data.channel.gt"] = "data.channel.gt"
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DataChannelGt":
        if self.in_power_metering and self.telemetry_name != SpaceheatTelemetryName.PowerW:
            raise ValueError(
                "Axiom 1 failed: telemetry_name must be PowerW when in_power_metering is true."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "DataChannelGt":
        expected = _TELEMETRY_QUANTITY_PROJECTION.get(self.telemetry_name)
        if expected is not None and self.quantity != expected:
            raise ValueError(
                "Axiom 2 failed: quantity is inconsistent with telemetry_name."
            )
        return self
