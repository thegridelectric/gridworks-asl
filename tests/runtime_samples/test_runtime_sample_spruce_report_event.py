import json
from pathlib import Path

import pytest

from sema.runtime.codec import default_codec
from sema.runtime.base import SemaError


def test_runtime_report_event_003() -> None:
    payload = json.loads(Path(__file__).with_name("report.event-003.json").read_text())["Payload"]
    with pytest.raises(SemaError, match="message_id must equal report.id"):
        default_codec.from_dict(payload)
