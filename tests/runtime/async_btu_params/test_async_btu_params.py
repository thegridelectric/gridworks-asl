import json
import re
from pathlib import Path

import pytest

from sema.runtime.base import SemaError, UpgradeRequiresContext
from sema.runtime.codec import default_codec
from sema.runtime.enums.pico_board_variant import PicoBoardVariant
from sema.runtime.types.old_versions.async_btu_params_000 import AsyncBtuParams000
from sema.runtime.types.async_btu_params import AsyncBtuParams


def _axiom_match(n: int) -> re.Pattern[str]:
    return re.compile(rf"axiom {n}", re.IGNORECASE)


def _load_fixture(name: str, version_dir: str) -> dict:
    fixture = Path(__file__).parent / "fixtures" / version_dir / name
    return json.loads(fixture.read_text())


def test_async_btu_params_latest_version_is_100() -> None:
    assert AsyncBtuParams.version_value() == "100"


def test_v000_wire_shape_decodes() -> None:
    """The shipped 000 wire shape, null CtChannelName and float CaptureOffsetS included."""
    decoded = default_codec.from_dict(
        _load_fixture("default.json", "v000"), auto_upgrade=False
    )

    assert isinstance(decoded, AsyncBtuParams000)
    assert decoded.ct_channel_name is None
    assert decoded.capture_offset_s == 41.5


def test_v000_does_not_upgrade_without_context() -> None:
    """A 000 message cannot know its board; the upgrade refuses rather than guesses."""
    decoded = default_codec.from_dict(
        _load_fixture("default.json", "v000"), auto_upgrade=False
    )
    assert isinstance(decoded, AsyncBtuParams000)

    with pytest.raises(UpgradeRequiresContext):
        decoded.upgrade()

    with pytest.raises(UpgradeRequiresContext):
        default_codec.from_dict(_load_fixture("default.json", "v000"))


def test_v100_default_loads() -> None:
    decoded = default_codec.from_dict(_load_fixture("default.json", "v100"))

    assert isinstance(decoded, AsyncBtuParams)
    assert decoded.pico_board_variant == PicoBoardVariant.PicoRaspberryWifi2040
    assert decoded.micropython_version == "1.24.1"
    assert decoded.capture_offset_s is None


def test_v100_unknown_board_coerces_to_unknown() -> None:
    """An out-of-vocabulary board value lands on Unknown, never on a real board."""
    raw = _load_fixture("default.json", "v100")
    raw["PicoBoardVariant"] = "Esp32Something"
    decoded = default_codec.from_dict(raw)

    assert isinstance(decoded, AsyncBtuParams)
    assert decoded.pico_board_variant == PicoBoardVariant.Unknown


@pytest.mark.parametrize("version_dir", ["v000", "v100"])
def test_axiom_1_read_ct_voltage_iff_ct_channel_name(version_dir: str) -> None:
    """ReadCtVoltage is true iff CtChannelName is present."""
    with pytest.raises(SemaError, match=_axiom_match(1)):
        default_codec.from_dict(_load_fixture("axiom_1.json", version_dir))
