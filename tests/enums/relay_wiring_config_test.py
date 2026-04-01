"""
Tests for enum relay.wiring.config.000
"""

from sema.runtime.enums import RelayWiringConfig


def test_relay_wiring_config() -> None:
    assert set(RelayWiringConfig.values()) == {
        "NormallyClosed",
        "NormallyOpen",
        "DoubleThrow",
    }
    assert RelayWiringConfig.default() == RelayWiringConfig.NormallyClosed
    assert RelayWiringConfig.enum_name() == "relay.wiring.config"
    assert RelayWiringConfig.enum_version() == "000"
