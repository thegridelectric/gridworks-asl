from typing import Literal

from pydantic import BaseModel, ConfigDict, StrictInt, model_validator

from sema.runtime.base import SemaType
from sema.runtime.property_format import HandleName, LeftRightDot, SpaceheatName, UTCMilliseconds, UUID4Str


class FsmAtomicReportSimpleAction(BaseModel):
    value: Literal[0, 1]

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )


class FsmAtomicReportI2cAction(BaseModel):
    i2c_bus: SpaceheatName
    address: StrictInt
    i2c_register: StrictInt
    bit: StrictInt
    value: StrictInt

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        populate_by_name=True,
        extra="forbid",
    )


class FsmAtomicReport(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.atomic.report/001"""

    machine_handle: HandleName
    state_enum: str
    report_type: Literal["Other", "Event", "Action"]
    action: FsmAtomicReportSimpleAction | FsmAtomicReportI2cAction | None = None
    event_enum: LeftRightDot | None = None
    event: str | None = None
    from_state: str | None = None
    to_state: str | None = None
    unix_time_ms: UTCMilliseconds
    trigger_id: UUID4Str
    type_name: Literal["fsm.atomic.report"] = "fsm.atomic.report"
    version: Literal["001"] = "001"

    model_config = ConfigDict(
        alias_generator=SemaType.model_config.get("alias_generator"),
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

    @model_validator(mode="after")
    def check_axiom_1(self) -> "FsmAtomicReport":
        if (self.report_type == "Action") != (self.action is not None):
            raise ValueError(
                "Axiom 1 failed: action must be present if and only if report_type is Action."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "FsmAtomicReport":
        event_fields_present = all(
            field is not None
            for field in (self.event_enum, self.event, self.from_state, self.to_state)
        )
        if (self.report_type == "Event") != event_fields_present:
            raise ValueError(
                "Axiom 2 failed: event fields must be present if and only if report_type is Event."
            )
        return self
