"""
Tests for enum temp.calc.method.000
"""

from sema.runtime.enums import TempCalcMethod


def test_temp_calc_method() -> None:
    assert set(TempCalcMethod.values()) == {
        "SimpleBetaForPico",
        "SimpleBeta",
    }
    assert TempCalcMethod.default() == TempCalcMethod.SimpleBeta
    assert TempCalcMethod.enum_name() == "temp.calc.method"
    assert TempCalcMethod.enum_version() == "000"
