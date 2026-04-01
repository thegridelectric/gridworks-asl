import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from sema.runtime.codec import default_codec


def test_runtime_layout_lite_011() -> None:
    payload = json.loads(Path(__file__).with_name("layout.lite-011.json").read_text())["Payload"]
    with pytest.raises(ValidationError, match="quantity is inconsistent with telemetry_name"):
        default_codec.from_dict(payload)
