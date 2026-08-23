from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.old_versions.report_001 import Report001
from sema.runtime.types.old_versions.report_event_002 import ReportEvent002


class ReportEvent000(SemaType):
    """Sema: https://schemas.electricity.works/types/report.event/000"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    report: Report001
    type_name: Literal["report.event"] = "report.event"
    version: str = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ReportEvent000":
        """
        Axiom 1: ReportIdentityPropagation
        MessageId SHALL equal Report.Id.
        """
        if self.message_id != self.report.id:
            raise ValueError("Axiom 1 failed: message_id must equal report.id.")
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "ReportEvent000":
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
    def check_axiom_3(self) -> "ReportEvent000":
        """
        Axiom 3: ReportSourcePropagation
        Src SHALL equal Report.FromGNodeAlias.
        """
        if self.src != self.report.from_g_node_alias:
            raise ValueError("Axiom 3 failed: src must equal report.from_g_node_alias.")
        return self

    def upgrade(self) -> ReportEvent002:
        """- Report: report:001 -> 002"""
        raise SemaType.upgrade_requires_context(
            "report.event:000 cannot be upgraded to report.event:002 without "
            "context: the nested Report is report:001, whose upgrade to "
            "report:002 requires context. JournalKeeper retains v000 messages "
            "at their own version."
        )
