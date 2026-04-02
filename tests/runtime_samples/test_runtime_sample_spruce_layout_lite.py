import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.layout_lite import LayoutLite


def test_runtime_layout_lite_012() -> None:
    payload = json.loads(Path(__file__).with_name("layout.lite-012.json").read_text())["Payload"]
    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, LayoutLite)
    assert decoded.version == "012"
    assert decoded.type_name == "layout.lite"
