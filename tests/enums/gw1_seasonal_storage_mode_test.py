"""
Tests for enum gw1.seasonal.storage.mode.000
"""

from sema.runtime.enums import Gw1SeasonalStorageMode


def test_gw1_seasonal_storage_mode() -> None:
    assert set(Gw1SeasonalStorageMode.values()) == {
        "AllTanks",
        "BufferOnly",
    }
    assert Gw1SeasonalStorageMode.default() == Gw1SeasonalStorageMode.AllTanks
    assert Gw1SeasonalStorageMode.enum_name() == "gw1.seasonal.storage.mode"
    assert Gw1SeasonalStorageMode.enum_version() == "000"
