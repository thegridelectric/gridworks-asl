"""
Tests for enum change.relay.state.000
"""

from sema.runtime.enums import ChangeRelayState


def test_change_relay_state() -> None:
    assert set(ChangeRelayState.values()) == {
        "CloseRelay",
        "OpenRelay",
    }
    assert ChangeRelayState.default() == ChangeRelayState.OpenRelay
    assert ChangeRelayState.enum_name() == "change.relay.state"
    assert ChangeRelayState.enum_version() == "000"
