import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.snapshot_spaceheat import SnapshotSpaceheat


def test_runtime_snapshot_spaceheat_003() -> None:
    payload = json.loads(Path(__file__).with_name("snapshot.spaceheat-003.json").read_text())["Payload"]
    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, SnapshotSpaceheat)
    assert decoded.version == "003"
    assert decoded.type_name == "snapshot.spaceheat"
