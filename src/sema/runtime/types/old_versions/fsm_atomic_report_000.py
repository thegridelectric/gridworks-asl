from typing import Literal

from pydantic import StrictInt

from sema.runtime.base import SemaType
from sema.runtime.enums.fsm_report_type import FsmReportType
from sema.runtime.enums.relay_energization_state import RelayEnergizationState
from sema.runtime.property_format import HandleName, LeftRightDot, UTCMilliseconds, UUID4Str
from sema.runtime.types.fsm_atomic_report import (  # noqa: PLC0415
            FsmAtomicReport as FsmAtomicReport001,
            FsmAtomicReportSimpleAction,
        )

class FsmAtomicReport000(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.atomic.report/000"""

    machine_handle: HandleName
    state_enum: str
    report_type: FsmReportType
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

    def upgrade(self) -> FsmAtomicReport001:
        """
        000 -> 001:
        - Remove ActionType
        - Action: scalar → structured variants (oneOf)
        """
        data = self.model_dump()
        data.pop("action_type", None)

        if self.report_type == FsmReportType.Action and self.action is not None:
            if self.action_type != "RelayPinSet":
                raise ValueError(
                    "FsmAtomicReport000.upgrade() only supports ActionType 'RelayPinSet'."
                )
            data["action"] = FsmAtomicReportSimpleAction(
                value=RelayEnergizationState(self.action)
            )

        data["version"] = "001"
        return FsmAtomicReport001.model_validate(data)
