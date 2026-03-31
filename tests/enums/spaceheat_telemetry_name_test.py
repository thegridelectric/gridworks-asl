"""
Tests for enum spaceheat.telemetry.name latest and old versions.
"""

from sema.registry.enums import SpaceheatTelemetryName
from sema.registry.enums.old_versions import SpaceheatTelemetryName006


LATEST_VALUES = {
    "Unknown",
    "PowerW",
    "RelayState",
    "WaterTempCTimes1000",
    "WaterTempFTimes1000",
    "GpmTimes100",
    "CurrentRmsMicroAmps",
    "GallonsTimes100",
    "VoltageRmsMilliVolts",
    "MilliWattHours",
    "MicroHz",
    "AirTempCTimes1000",
    "AirTempFTimes1000",
    "ThermostatState",
    "MicroVolts",
    "VoltsTimesTen",
    "WattHours",
    "StorageLayer",
    "PercentKeep",
    "CelsiusTimes100",
    "VoltsTimes100",
    "HzTimes100",
    "BinaryState",
}


def test_spaceheat_telemetry_name_latest() -> None:
    assert set(SpaceheatTelemetryName.values()) == LATEST_VALUES
    assert SpaceheatTelemetryName.default() == SpaceheatTelemetryName.Unknown
    assert SpaceheatTelemetryName.enum_name() == "spaceheat.telemetry.name"
    assert SpaceheatTelemetryName.enum_version() == "007"


def test_spaceheat_telemetry_name_006() -> None:
    assert set(SpaceheatTelemetryName006.values()) == (LATEST_VALUES - {"BinaryState"})
    assert SpaceheatTelemetryName006.default() == SpaceheatTelemetryName006.Unknown
    assert SpaceheatTelemetryName006.enum_name() == "spaceheat.telemetry.name"
    assert SpaceheatTelemetryName006.enum_version() == "006"
