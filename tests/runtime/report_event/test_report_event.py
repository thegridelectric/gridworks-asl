import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.report_event import ReportEvent


def test_report_event_latest_version_is_004() -> None:
    assert ReportEvent.version_value() == "004"


def test_default_v002_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, ReportEvent)
    assert decoded.type_name == "report.event"
    assert decoded.version == "004"


def test_default_v003_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v003" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, ReportEvent)
    assert decoded.type_name == "report.event"
    assert decoded.version == "004"


def test_default_v004_loads_as_report_event() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v004" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, ReportEvent)
    assert decoded.type_name == "report.event"
    assert decoded.version == "004"
