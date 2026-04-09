from typing import Literal

from pydantic import model_validator

from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot, UTCMilliseconds, UUID4Str
from sema.runtime.types.report import Report


class ReportEvent(SemaType):
    """Sema: https://schemas.electricity.works/types/report.event/003"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    report: Report
    type_name: Literal["report.event"] = "report.event"
    version: Literal["003"] = "003"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ReportEvent":
        if self.message_id != self.report.id:
            raise ValueError(f"Axiom 1 failed: message_id {self.message_id} must equal report.id {self.report.id}.")
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "ReportEvent":
        if self.time_created_ms != self.report.message_created_ms:
            raise ValueError(
                f"Axiom 2 failed: time_created_ms {self.time_created_ms} equal report.message_created_ms {self.report.message_created_ms}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "ReportEvent":
        if self.src != self.report.from_g_node_alias:
            raise ValueError(f"Axiom 3 failed: src {self.src} must equal report.from_g_node_alias {self.report.from_g_node_alias}.")
        return self
