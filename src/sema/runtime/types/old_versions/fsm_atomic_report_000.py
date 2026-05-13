from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import FsmReportType
from sema.runtime.enums import RelayEnergizationState
from sema.runtime.property_format import HandleName
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.fsm_atomic_report import FsmAtomicReport


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

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "FsmAtomicReport000":
        """
        Axiom 1: ActionPresenceConsistency
        Action and ActionType SHALL be present if and only if ReportType equals Action.
        """
        is_action = self.report_type == FsmReportType.Action
        action_fields_present = self.action is not None and self.action_type is not None
        if is_action != action_fields_present:
            raise ValueError(
                "Axiom 1 failed: action and action_type must be present iff "
                "report_type is Action."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "FsmAtomicReport000":
        """
        Axiom 2: ActionTypeConsistency
        If Action is present, ActionType SHALL also be present.
        """
        if self.action is not None and self.action_type is None:
            raise ValueError(
                "Axiom 2 failed: if action is present, action_type must also be present."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "FsmAtomicReport000":
        """
        Axiom 3: EventPresenceConsistency
        EventEnum, Event, FromState, and ToState SHALL be present if and only if ReportType
        equals Event.
        """
        is_event = self.report_type == FsmReportType.Event
        event_fields_present = (
            self.event_enum is not None
            and self.event is not None
            and self.from_state is not None
            and self.to_state is not None
        )
        if is_event != event_fields_present:
            raise ValueError(
                "Axiom 3 failed: event_enum, event, from_state, and to_state must be "
                "present iff report_type is Event."
            )
        return self

    def upgrade(self) -> FsmAtomicReport:
        """
        - ActionType: remove
        - Action: scalar -> unconstrained object payload
        """
        data = self.model_dump()
        data.pop("action_type", None)

        if self.report_type == FsmReportType.Action and self.action is not None:
            if self.action_type != "RelayPinSet":
                raise ValueError(
                    "FsmAtomicReport000.upgrade() only supports ActionType 'RelayPinSet'."
                )
            data["action"] = {
                "Value": RelayEnergizationState(self.action).value
            }

        data["version"] = "001"
        return FsmAtomicReport.model_validate(data)
