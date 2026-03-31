from pydantic import ValidationError

from sema.registry.types.report import Report
from sema.registry.types.report_event import ReportEvent


def test_report_event_propagation_axioms() -> None:
    report = Report(
        from_g_node_alias="d1.isone.me.versant.keene.peach.scada",
        from_g_node_instance_id=str(__import__("uuid").uuid4()),
        about_g_node_alias="d1.isone.me.versant.keene.peach.ta",
        slot_start_unix_s=1735689600,
        slot_duration_s=300,
        channel_reading_list=[],
        state_list=[],
        fsm_report_list=[],
        message_created_ms=1735689600123,
        id=str(__import__("uuid").uuid4()),
    )
    try:
        ReportEvent(
            message_id=str(__import__("uuid").uuid4()),
            time_created_ms=1735689600123,
            src="d1.isone.me.versant.keene.peach.scada",
            report=report,
        )
    except ValidationError:
        return
    raise AssertionError("Expected validation failure")
