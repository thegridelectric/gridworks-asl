"""
Tests for enum recognized.currency.unit.000
"""

from sema.registry.enums import RecognizedCurrencyUnit


def test_recognized_currency_unit() -> None:
    assert set(RecognizedCurrencyUnit.values()) == {
        "UNKNOWN",
        "USD",
        "GBP",
    }

    assert RecognizedCurrencyUnit.default() == RecognizedCurrencyUnit.UNKNOWN
    assert RecognizedCurrencyUnit.enum_name() == "recognized.currency.unit"
    assert RecognizedCurrencyUnit.enum_version() == "000"

