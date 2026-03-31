import pytest

from sema.registry.base import SemaError
from runtime_sample_test_helpers import decode_runtime_payload


def test_runtime_sample_beech_layout_lite() -> None:
    with pytest.raises(SemaError, match="quantity is inconsistent with telemetry_name"):
        decode_runtime_payload(
            "gridworks-scada-dev/"
            "hw1.isone.me.versant.keene.beech.scada-layout.lite-1774957232033-ear.electricity.works.json"
        )
