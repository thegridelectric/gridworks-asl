"""i2c.write.reg axiom counterexamples — sema must reject what violates an axiom."""

import json
from pathlib import Path

import pytest

from sema.runtime.base import SemaError
from sema.runtime.codec import default_codec

FIX = Path(__file__).parent / "fixtures" / "v000"


def test_axiom_1_catches_num_bytes_out_of_range() -> None:
    payload = json.loads((FIX / "axiom_1.json").read_text())
    with pytest.raises(SemaError, match="NumBytesRange"):
        default_codec.from_dict(payload)


def test_axiom_2_catches_value_too_big_for_num_bytes() -> None:
    payload = json.loads((FIX / "axiom_2.json").read_text())
    with pytest.raises(SemaError, match="ValueFitsNumBytes"):
        default_codec.from_dict(payload)
