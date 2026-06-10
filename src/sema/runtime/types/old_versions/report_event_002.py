from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.report_002 import Report002
from sema.runtime.types.report_event import ReportEvent


class ReportEvent002(SemaType):
    """Sema: https://schemas.electricity.works/types/report.event/002"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    report: Report002
    type_name: Literal["report.event"] = "report.event"
    version: str = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ReportEvent002":
        """
        Axiom 1: ReportIdentityPropagation
        MessageId SHALL equal Report.Id.
        """
        if self.message_id != self.report.id:
            raise ValueError("Axiom 1 failed: message_id must equal report.id.")
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "ReportEvent002":
        """
        Axiom 2: ReportCreatedTimePropagation
        TimeCreatedMs SHALL equal Report.MessageCreatedMs.
        """
        if self.time_created_ms != self.report.message_created_ms:
            raise ValueError(
                "Axiom 2 failed: time_created_ms must equal report.message_created_ms."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "ReportEvent002":
        """
        Axiom 3: ReportSourcePropagation
        Src SHALL equal Report.FromGNodeAlias.
        """
        if self.src != self.report.from_g_node_alias:
            raise ValueError("Axiom 3 failed: src must equal report.from_g_node_alias.")
        return self

    def upgrade(self) -> ReportEvent:
        """
        - Report: report:002 -> 003
        - Axioms: remove former ReportIdentityPropagation and ReportCreatedTimePropagation
        """
        data = self.model_dump()
        data["report"] = self.report.upgrade()
        data["version"] = "003"
        return ReportEvent.model_validate(data)
