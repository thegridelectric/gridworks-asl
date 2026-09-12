import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec
from sema.runtime.types.baseurl_failure_alert import BaseurlFailureAlert


def _load_fixture(name: str, version_dir: str) -> dict:
    fixture = Path(__file__).parent / "fixtures" / version_dir / name
    return json.loads(fixture.read_text())


def test_baseurl_failure_alert_latest_version_is_100() -> None:
    assert BaseurlFailureAlert.version_value() == "100"


def test_v100_default_loads() -> None:
    decoded = default_codec.from_dict(_load_fixture("default.json", "v100"))

    assert isinstance(decoded, BaseurlFailureAlert)
    assert decoded.hw_uid == "pico_3a202a"
    assert decoded.base_url == "http://192.168.0.10:8080"


def test_actor_node_name_is_spaceheat_name() -> None:
    raw = _load_fixture("default.json", "v100")
    raw["ActorNodeName"] = "Primary_BTU"
    with pytest.raises(SemaError):
        default_codec.from_dict(raw)
