"""
Tests for enum gw1.quantity latest and old versions.
"""

from sema.registry.enums import Gw1Quantity
from sema.registry.enums.old_versions import Gw1Quantity000


def test_gw1_quantity_latest() -> None:
    assert set(Gw1Quantity.values()) == {
        "Unknown",
        "Unitless",
        "Power",
        "Energy",
        "Temperature",
        "FlowRate",
        "Volume",
        "Voltage",
        "Current",
        "Percent",
        "Frequency",
        "Time",
    }
    assert Gw1Quantity.default() == Gw1Quantity.Unknown
    assert Gw1Quantity.enum_name() == "gw1.quantity"
    assert Gw1Quantity.enum_version() == "001"


def test_gw1_quantity_000() -> None:
    assert set(Gw1Quantity000.values()) == {
        "Unknown",
        "Unitless",
        "Power",
        "Energy",
        "Temperature",
        "FlowRate",
        "Volume",
        "Voltage",
        "Current",
        "Percent",
        "Frequency",
    }
    assert Gw1Quantity000.default() == Gw1Quantity000.Unknown
    assert Gw1Quantity000.enum_name() == "gw1.quantity"
    assert Gw1Quantity000.enum_version() == "000"
