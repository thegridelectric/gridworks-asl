"""
Tests for enum gw1.system.mode.000
"""

from sema.runtime.enums import Gw1SystemMode


def test_gw1_system_mode() -> None:
    assert set(Gw1SystemMode.values()) == {
        "Heating",
        "Standby",
        "MonitorOnly",
    }
    assert Gw1SystemMode.default() == Gw1SystemMode.Heating
    assert Gw1SystemMode.enum_name() == "gw1.system.mode"
    assert Gw1SystemMode.enum_version() == "000"
