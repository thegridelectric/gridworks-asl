from typing import Literal

from pydantic import model_validator

from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_quantity_000 import Gw1Quantity000
from sema.runtime.enums.spaceheat_telemetry_name import SpaceheatTelemetryName


_PROJECTION = {
    SpaceheatTelemetryName.Unknown: Gw1Quantity000.Unknown,
    SpaceheatTelemetryName.PowerW: Gw1Quantity000.Power,
    SpaceheatTelemetryName.WattHours: Gw1Quantity000.Energy,
    SpaceheatTelemetryName.MilliWattHours: Gw1Quantity000.Energy,
    SpaceheatTelemetryName.WaterTempCTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName.WaterTempFTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName.AirTempCTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName.AirTempFTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName.CelsiusTimes100: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName.GpmTimes100: Gw1Quantity000.FlowRate,
    SpaceheatTelemetryName.GallonsTimes100: Gw1Quantity000.Volume,
    SpaceheatTelemetryName.VoltageRmsMilliVolts: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName.VoltsTimesTen: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName.VoltsTimes100: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName.MicroVolts: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName.CurrentRmsMicroAmps: Gw1Quantity000.Current,
    SpaceheatTelemetryName.HzTimes100: Gw1Quantity000.Frequency,
    SpaceheatTelemetryName.MicroHz: Gw1Quantity000.Frequency,
    SpaceheatTelemetryName.RelayState: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName.ThermostatState: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName.StorageLayer: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName.BinaryState: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName.PercentKeep: Gw1Quantity000.Percent,
}


class SpaceheatTelemetryQuantityProjection(SemaType):
    """Sema: https://schemas.electricity.works/types/spaceheat.telemetry.quantity.projection/000"""

    telemetry_name: SpaceheatTelemetryName
    quantity: Gw1Quantity000
    type_name: Literal["spaceheat.telemetry.quantity.projection"] = "spaceheat.telemetry.quantity.projection"
    version: Literal["000"] = "000"

    @classmethod
    def project(cls, telemetry_name: SpaceheatTelemetryName) -> Gw1Quantity000:
        expected = _PROJECTION.get(telemetry_name)
        if expected is None:
            raise ValueError(
                f"No quantity projection defined for telemetry_name {telemetry_name!r}."
            )
        return expected

    @model_validator(mode="after")
    def check_axiom_1(self) -> "SpaceheatTelemetryQuantityProjection":
        expected = self.project(self.telemetry_name)
        if expected != self.quantity:
            raise ValueError(
                "Axiom 1 failed: telemetry_name and quantity do not match the enumerated projection."
            )
        return self
