import json
from pathlib import Path

from sema.runtime.codec import default_codec
from sema.runtime.types.fsm_atomic_report import FsmAtomicReport


def test_fsm_atomic_report_latest_version_is_001() -> None:
    assert FsmAtomicReport.version_value() == "001"


def test_default_v000_upgrades_to_latest() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v000" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, FsmAtomicReport)
    assert decoded.type_name == "fsm.atomic.report"
    assert decoded.version == "001"


def test_default_v001_loads_as_fsm_atomic_report() -> None:
    fixture = Path(__file__).parent / "fixtures" / "v001" / "default.json"
    payload = json.loads(fixture.read_text())

    decoded = default_codec.from_dict(payload)

    assert isinstance(decoded, FsmAtomicReport)
    assert decoded.type_name == "fsm.atomic.report"
    assert decoded.version == "001"
