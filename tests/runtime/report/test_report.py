import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.report import Report


def test_report_latest_version_is_003() -> None:
    assert Report.version_value() == "003"


def test_default_v002_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, Report)
    assert decoded.type_name == "report"
    assert decoded.version == "003"


def test_default_v003_loads_as_report() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v003" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, Report)
    assert decoded.type_name == "report"
    assert decoded.version == "003"
