import json
from pathlib import Path

import pytest

from sema.runtime.base import UpgradeRequiresContext
from sema.runtime.codec import default_codec
from sema.runtime.types.i2c_multichannel_dt_relay_component_gt import (
    I2cMultichannelDtRelayComponentGt,
)


def test_i2c_multichannel_dt_relay_component_gt_latest_version_is_004() -> None:
    assert I2cMultichannelDtRelayComponentGt.version_value() == "004"


def test_default_v002_decode_requires_context() -> None:
    # 003 -> 004 (cac_id -> DeviceType) is a context-dependent upgrade: a standalone
    # old-version message cannot climb to latest without the source layout, which is
    # where DeviceType is carried. The codec surfaces this as UpgradeRequiresContext.
    fixture = Path(__file__).parent / "fixtures" / "v002" / "default.json"
    payload = json.loads(fixture.read_text())
    with pytest.raises(UpgradeRequiresContext):
        default_codec.from_dict(payload)


def test_default_v003_decode_requires_context() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v003" / "default.json"
    payload = json.loads(fixture.read_text())
    with pytest.raises(UpgradeRequiresContext):
        default_codec.from_dict(payload)
