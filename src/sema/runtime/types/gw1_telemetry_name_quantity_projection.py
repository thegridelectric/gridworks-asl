from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums.old_versions.gw1_quantity_000 import Gw1Quantity000
from sema.runtime.enums.old_versions.spaceheat_telemetry_name_006 import SpaceheatTelemetryName006


_PROJECTION = {
    SpaceheatTelemetryName006.Unknown: Gw1Quantity000.Unknown,
    SpaceheatTelemetryName006.PowerW: Gw1Quantity000.Power,
    SpaceheatTelemetryName006.WattHours: Gw1Quantity000.Energy,
    SpaceheatTelemetryName006.MilliWattHours: Gw1Quantity000.Energy,
    SpaceheatTelemetryName006.WaterTempCTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName006.WaterTempFTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName006.AirTempCTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName006.AirTempFTimes1000: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName006.CelsiusTimes100: Gw1Quantity000.Temperature,
    SpaceheatTelemetryName006.GpmTimes100: Gw1Quantity000.FlowRate,
    SpaceheatTelemetryName006.GallonsTimes100: Gw1Quantity000.Volume,
    SpaceheatTelemetryName006.VoltageRmsMilliVolts: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName006.VoltsTimesTen: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName006.VoltsTimes100: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName006.MicroVolts: Gw1Quantity000.Voltage,
    SpaceheatTelemetryName006.CurrentRmsMicroAmps: Gw1Quantity000.Current,
    SpaceheatTelemetryName006.HzTimes100: Gw1Quantity000.Frequency,
    SpaceheatTelemetryName006.MicroHz: Gw1Quantity000.Frequency,
    SpaceheatTelemetryName006.RelayState: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName006.ThermostatState: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName006.StorageLayer: Gw1Quantity000.Unitless,
    SpaceheatTelemetryName006.PercentKeep: Gw1Quantity000.Percent,
}


class Gw1TelemetryNameQuantityProjection(SemaType):
    """Sema: https://schemas.electricity.works/types/gw1.telemetry.name.quantity.projection/000"""

    telemetry_name: SpaceheatTelemetryName006
    quantity: Gw1Quantity000
    type_name: Literal["gw1.telemetry.name.quantity.projection"] = "gw1.telemetry.name.quantity.projection"
    version: Literal["000"] = "000"

    @classmethod
    def project(cls, telemetry_name: SpaceheatTelemetryName006) -> Gw1Quantity000:
        expected = _PROJECTION.get(telemetry_name)
        if expected is None:
            raise ValueError(
                f"No projection defined for telemetry_name {telemetry_name!r}."
            )
        return expected

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Gw1TelemetryNameQuantityProjection":
        """
        Axiom 1: EnumeratedTelemetryProjectionMapping
        Every (TelemetryName, Quantity) pair SHALL match the mapping declared in
        x-gridworks.projection.table. Any other combination is invalid.
        """
        expected = self.project(self.telemetry_name)
        if expected != self.quantity:
            raise ValueError(
                "Axiom 1 failed: telemetry_name and quantity do not match the enumerated projection."
            )
        return self
