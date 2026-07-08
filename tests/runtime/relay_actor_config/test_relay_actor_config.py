import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.relay_actor_config import RelayActorConfig


def test_relay_actor_config_latest_version_is_003() -> None:
    assert RelayActorConfig.version_value() == "004"


def test_real_beech_v002_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v002" / "real_beech.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, RelayActorConfig)
    assert decoded.type_name == "relay.actor.config"
    assert decoded.version == "004"


def test_default_v003_loads_as_relay_actor_config() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v003" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, RelayActorConfig)
    assert decoded.type_name == "relay.actor.config"
    assert decoded.version == "004"
