"""
Tests for enum gw1.emission.method.000
"""

from sema.runtime.enums import Gw1EmissionMethod


def test_gw1_emission_method() -> None:
    assert set(Gw1EmissionMethod.values()) == {
        "OnTrigger",
        "Periodic",
        "AsyncAndPeriodic",
    }
    assert Gw1EmissionMethod.default() == Gw1EmissionMethod.OnTrigger
    assert Gw1EmissionMethod.enum_name() == "gw1.emission.method"
    assert Gw1EmissionMethod.enum_version() == "000"
