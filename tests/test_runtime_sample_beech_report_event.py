from sema.registry.types.report_event import ReportEvent
from runtime_sample_test_helpers import decode_runtime_payload


def test_runtime_sample_beech_report_event() -> None:
    decoded = decode_runtime_payload(
        "gridworks-scada-dev/"
        "hw1.isone.me.versant.keene.beech.scada-report.event-1774915500457-ear.electricity.works.json"
    )

    assert isinstance(decoded, ReportEvent)
    assert decoded.version == "003"
    assert decoded.type_name == "report.event"
