import json
from pathlib import Path

import pytest

from sema.runtime.base import UpgradeRequiresContext
from sema.runtime.codec import default_codec
from sema.runtime.types.layout_lite import LayoutLite


def test_layout_lite_latest_version_is_013() -> None:
    assert LayoutLite.version_value() == "013"


def test_real_beech_v011_to_latest_requires_context() -> None:
    # 012 -> 013 migrates the embedded components cac_id -> DeviceType (and the
    # SystemMode -> ActuationAuthority x ServiceMode split), a context-dependent
    # upgrade, so a standalone old projection cannot climb to latest without the
    # source layout. The scada instead emits a fresh /013 on boot.
    fixture = Path(__file__).parent / "fixtures" / "v011" / "real_beech.json"
    payload = json.loads(fixture.read_text())
    with pytest.raises(UpgradeRequiresContext):
        default_codec.from_dict(payload)


def test_real_spruce_v012_to_latest_requires_context() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v012" / "real_spruce.json"
    payload = json.loads(fixture.read_text())
    with pytest.raises(UpgradeRequiresContext):
        default_codec.from_dict(payload)
