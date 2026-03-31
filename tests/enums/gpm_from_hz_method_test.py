"""
Tests for enum gpm.from.hz.method.000
"""

from sema.registry.enums import GpmFromHzMethod


def test_gpm_from_hz_method() -> None:
    assert set(GpmFromHzMethod.values()) == {
        "Constant",
    }
    assert GpmFromHzMethod.default() == GpmFromHzMethod.Constant
    assert GpmFromHzMethod.enum_name() == "gpm.from.hz.method"
    assert GpmFromHzMethod.enum_version() == "000"
