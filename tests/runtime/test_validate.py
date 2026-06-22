"""Tests for the `sema.runtime.validate` API (and the `sema validate` CLI surface)."""

from sema.runtime.validate import validate

GOOD = {
    "ChannelName": "scada",
    "CapturePeriodS": 1,
    "AsyncCapture": False,
    "Exponent": 0,
    "Unit": "Unknown",
    "TypeName": "channel.config",
    "Version": "000",
}


def test_validate_ok() -> None:
    r = validate(GOOD)
    assert r.ok
    assert r.type_name == "channel.config"
    assert r.error is None


def test_validate_accepts_json_text() -> None:
    import json

    assert validate(json.dumps(GOOD)).ok


def test_validate_rejects_bad_value() -> None:
    r = validate({**GOOD, "CapturePeriodS": -5})
    assert not r.ok
    assert "CapturePeriodS" in (r.error or "")


def test_validate_rejects_unknown_type() -> None:
    r = validate({"TypeName": "no.such.type", "Version": "000"})
    assert not r.ok
    assert r.type_name == "no.such.type"


def test_validate_expected_type_mismatch() -> None:
    r = validate(GOOD, expected_type="i2c.result")
    assert not r.ok
    assert "Expected TypeName" in (r.error or "")


def test_validate_non_object() -> None:
    assert not validate("[]").ok
