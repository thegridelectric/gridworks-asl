"""
Tests for enum spaceheat.unit.001
"""

from sema.runtime.enums import SpaceheatUnit


def test_spaceheat_unit() -> None:
    assert set(SpaceheatUnit.values()) == {
        "Unknown",
        "Unitless",
        "W",
        "Celcius",
        "Fahrenheit",
        "Gpm",
        "WattHours",
        "AmpsRms",
        "VoltsRms",
        "Gallons",
        "ThermostatStateEnum",
    }
    assert SpaceheatUnit.default() == SpaceheatUnit.Unknown
    assert SpaceheatUnit.enum_name() == "spaceheat.unit"
    assert SpaceheatUnit.enum_version() == "001"
