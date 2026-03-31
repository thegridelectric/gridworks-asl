from typing import Literal

from sema.registry.base import SemaType
from sema.registry.property_format import HandleName, LeftRightDot, UTCMilliseconds, UUID4Str


class FsmAtomicReport000(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.atomic.report/000"""

    machine_handle: HandleName
    state_enum: str
    report_type: str
    action_type: str | None = None
    action: int | None = None
    event_enum: LeftRightDot | None = None
    event: str | None = None
    from_state: str | None = None
    to_state: str | None = None
    unix_time_ms: UTCMilliseconds
    trigger_id: UUID4Str
    type_name: Literal["fsm.atomic.report"] = "fsm.atomic.report"
    version: Literal["000"] = "000"

    def to_latest(self) -> "FsmAtomicReport":
        from sema.registry.types.fsm_atomic_report import (  # noqa: PLC0415
            FsmAtomicReport,
            FsmAtomicReportSimpleAction,
        )

        action = None
        if self.report_type == "Action" and self.action is not None:
            action = FsmAtomicReportSimpleAction(value=self.action)

        return FsmAtomicReport(
            machine_handle=self.machine_handle,
            state_enum=self.state_enum,
            report_type=self.report_type,
            action=action,
            event_enum=self.event_enum,
            event=self.event,
            from_state=self.from_state,
            to_state=self.to_state,
            unix_time_ms=self.unix_time_ms,
            trigger_id=self.trigger_id,
        )
