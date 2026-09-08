import json
import re
from pathlib import Path

import pytest

from sema.runtime.base import SemaError, UpgradeRequiresContext
from sema.runtime.codec import default_codec
from sema.runtime.enums.pico_board_variant import PicoBoardVariant
from sema.runtime.types.old_versions.tank_module_params_110 import TankModuleParams110
from sema.runtime.types.tank_module_params import TankModuleParams


def _axiom_match(n: int) -> re.Pattern[str]:
    return re.compile(rf"axiom {n}", re.IGNORECASE)


def _load_fixture(name: str, version_dir: str) -> dict:
    fixture = Path(__file__).parent / "fixtures" / version_dir / name
    return json.loads(fixture.read_text())


def test_tank_module_params_latest_version_is_200() -> None:
    assert TankModuleParams.version_value() == "200"


def test_v110_wire_shape_decodes() -> None:
    """The shipped 110 wire shape, null PicoAB and float CaptureOffsetS included."""
    decoded = default_codec.from_dict(
        _load_fixture("default.json", "v110"), auto_upgrade=False
    )

    assert isinstance(decoded, TankModuleParams110)
    assert decoded.pico_a_b is None
    assert decoded.capture_offset_s == 41.5


def test_v110_does_not_upgrade_without_context() -> None:
    """A 110 message cannot know its board; the upgrade refuses rather than guesses."""
    decoded = default_codec.from_dict(
        _load_fixture("default.json", "v110"), auto_upgrade=False
    )
    assert isinstance(decoded, TankModuleParams110)

    with pytest.raises(UpgradeRequiresContext):
        decoded.upgrade()

    with pytest.raises(UpgradeRequiresContext):
        default_codec.from_dict(_load_fixture("default.json", "v110"))


def test_v200_default_loads() -> None:
    decoded = default_codec.from_dict(_load_fixture("default.json", "v200"))

    assert isinstance(decoded, TankModuleParams)
    assert decoded.pico_board_variant == PicoBoardVariant.PicoRaspberryWifi2040
    assert decoded.micropython_version == "1.24.1"
    assert decoded.capture_offset_s is None


def test_v200_unknown_board_coerces_to_unknown() -> None:
    """An out-of-vocabulary board value lands on Unknown, never on a real board."""
    raw = _load_fixture("default.json", "v200")
    raw["PicoBoardVariant"] = "Esp32Something"
    decoded = default_codec.from_dict(raw)

    assert isinstance(decoded, TankModuleParams)
    assert decoded.pico_board_variant == PicoBoardVariant.Unknown


@pytest.mark.parametrize("version_dir", ["v110", "v200"])
def test_axiom_1_pico_a_b_is_a_or_b(version_dir: str) -> None:
    """If PicoAB is present it SHALL be "a" or "b"."""
    with pytest.raises(SemaError, match=_axiom_match(1)):
        default_codec.from_dict(_load_fixture("axiom_1.json", version_dir))
