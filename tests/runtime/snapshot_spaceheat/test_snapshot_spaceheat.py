import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.snapshot_spaceheat import SnapshotSpaceheat


def test_snapshot_spaceheat_latest_version_is_003() -> None:
    assert SnapshotSpaceheat.version_value() == "003"


def test_real_spruce_v003_loads_as_snapshot_spaceheat() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v003" / "real_spruce.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, SnapshotSpaceheat)
    assert decoded.type_name == "snapshot.spaceheat"
    assert decoded.version == "003"
