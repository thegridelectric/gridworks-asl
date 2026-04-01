from typing import Literal

from pydantic import StrictInt

from sema.runtime.base import SemaType
from sema.runtime.property_format import HandleName, LeftRightDot, UTCMilliseconds, UUID4Str
from sema.runtime.types.fsm_atomic_report import (  # noqa: PLC0415
            FsmAtomicReport,
            FsmAtomicReportSimpleAction,
        )

class FsmAtomicReport000(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.atomic.report/000"""

    machine_handle: HandleName
    state_enum: str
    report_type: str
    action_type: str | None = None
    action: StrictInt | None = None
    event_enum: LeftRightDot | None = None
    event: str | None = None
    from_state: str | None = None
    to_state: str | None = None
    unix_time_ms: UTCMilliseconds
    trigger_id: UUID4Str
    type_name: Literal["fsm.atomic.report"] = "fsm.atomic.report"
    version: Literal["000"] = "000"

    def upgrade(self) -> FsmAtomicReport:
        """ TODO: ADD DOCSTRING"""

        action = None
        report_type = "Other"
        if self.report_type == "Action" and self.action is not None:
            report_type = "Action"
            if self.action == 0:
                action = FsmAtomicReportSimpleAction(value=0)
            else:
                action = FsmAtomicReportSimpleAction(value=1)
        elif self.report_type == "Event":
            report_type = "Event"

        return FsmAtomicReport(
            machine_handle=self.machine_handle,
            state_enum=self.state_enum,
            report_type=report_type,
            action=action,
            event_enum=self.event_enum,
            event=self.event,
            from_state=self.from_state,
            to_state=self.to_state,
            unix_time_ms=self.unix_time_ms,
            trigger_id=self.trigger_id,
        )
