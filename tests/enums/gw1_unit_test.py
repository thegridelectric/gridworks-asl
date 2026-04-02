"""
Tests for enum gw1.unit latest and old versions.
"""

from sema.runtime.enums import Gw1Unit
from sema.runtime.enums.old_versions import Gw1Unit000


def test_gw1_unit_latest() -> None:
    assert set(Gw1Unit.values()) == {
        "Unknown",
        "Unitless",
        "FahrenheitX100",
        "Watts",
        "WattHours",
        "Gallons",
        "GpmX100",
        "Seconds",
        "SecondsX10",
    }
    assert Gw1Unit.default() == Gw1Unit.Unknown
    assert Gw1Unit.enum_name() == "gw1.unit"
    assert Gw1Unit.enum_version() == "001"


def test_gw1_unit_000() -> None:
    assert set(Gw1Unit000.values()) == {
        "Unknown",
        "Unitless",
        "FahrenheitX100",
        "Watts",
        "WattHours",
        "Gallons",
        "GpmX100",
    }
    assert Gw1Unit000.default() == Gw1Unit000.Unknown
    assert Gw1Unit000.enum_name() == "gw1.unit"
    assert Gw1Unit000.enum_version() == "000"
