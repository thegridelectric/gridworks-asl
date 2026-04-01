import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.report_event import ReportEvent


def test_runtime_report_event_002() -> None:
    payload = json.loads(Path(__file__).with_name("report.event-002.json").read_text())["Payload"]
    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, ReportEvent)
    assert decoded.version == "003"
    assert decoded.type_name == "report.event"
