import pytest

from sema.registry.base import SemaError
from runtime_sample_test_helpers import decode_runtime_payload


def test_runtime_sample_spruce_report_event() -> None:
    with pytest.raises(SemaError, match="message_id must equal report.id"):
        decode_runtime_payload(
            "gridworks-scada-jm-spruce/"
            "hw1.isone.me.versant.keene.spruce.scada-report.event-1774956900112-ear.electricity.works.json"
        )
