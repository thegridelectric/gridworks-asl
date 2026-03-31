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
