"""
Tests for enum gw1.float.unit.000
"""

from sema.runtime.enums import Gw1FloatUnit


def test_gw1_float_unit() -> None:
    assert set(Gw1FloatUnit.values()) == {
        "Seconds",
        "Milliseconds",
        "Fahrenheit",
        "Celsius",
        "Watts",
        "WattHours",
        "Gallons",
        "GallonsPerMinute",
    }
    assert Gw1FloatUnit.default() == Gw1FloatUnit.Watts
    assert Gw1FloatUnit.enum_name() == "gw1.float.unit"
    assert Gw1FloatUnit.enum_version() == "000"
