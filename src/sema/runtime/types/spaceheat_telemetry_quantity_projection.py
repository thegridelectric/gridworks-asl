from typing import Literal

from pydantic import model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.gw1_quantity import Gw1Quantity
from sema.runtime.enums.spaceheat_telemetry_name import SpaceheatTelemetryName


_PROJECTION = {
    SpaceheatTelemetryName.Unknown: Gw1Quantity.Unknown,
    SpaceheatTelemetryName.PowerW: Gw1Quantity.Power,
    SpaceheatTelemetryName.WattHours: Gw1Quantity.Energy,
    SpaceheatTelemetryName.MilliWattHours: Gw1Quantity.Energy,
    SpaceheatTelemetryName.WaterTempCTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.WaterTempFTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.AirTempCTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.AirTempFTimes1000: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.CelsiusTimes100: Gw1Quantity.Temperature,
    SpaceheatTelemetryName.GpmTimes100: Gw1Quantity.FlowRate,
    SpaceheatTelemetryName.GallonsTimes100: Gw1Quantity.Volume,
    SpaceheatTelemetryName.VoltageRmsMilliVolts: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.VoltsTimesTen: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.VoltsTimes100: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.MicroVolts: Gw1Quantity.Voltage,
    SpaceheatTelemetryName.CurrentRmsMicroAmps: Gw1Quantity.Current,
    SpaceheatTelemetryName.HzTimes100: Gw1Quantity.Frequency,
    SpaceheatTelemetryName.MicroHz: Gw1Quantity.Frequency,
    SpaceheatTelemetryName.RelayState: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.ThermostatState: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.StorageLayer: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.BinaryState: Gw1Quantity.Unitless,
    SpaceheatTelemetryName.PercentKeep: Gw1Quantity.Percent,
}


class SpaceheatTelemetryQuantityProjection(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.telemetry.quantity.projection/000"""

    telemetry_name: SpaceheatTelemetryName
    quantity: Gw1Quantity
    type_name: Literal["spaceheat.telemetry.quantity.projection"] = "spaceheat.telemetry.quantity.projection"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SpaceheatTelemetryQuantityProjection":
        expected = _PROJECTION.get(self.telemetry_name)
        if expected != self.quantity:
            raise ValueError(
                "Axiom 1 failed: telemetry_name and quantity do not match the enumerated projection."
            )
        return self
