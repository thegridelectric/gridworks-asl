from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.report import Report
from sema.runtime.types.report_event import ReportEvent


class ReportEvent003(SemaType):
    """Sema: https://schemas.electricity.works/types/report.event/003"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    report: Report
    type_name: Literal["report.event"] = "report.event"
    version: Literal["003"] = "003"

    @model_validator(mode="after")
    def check_axiom_3(self) -> "ReportEvent003":
        """
        Axiom 3: ReportSourcePropagation
        Src SHALL equal Report.FromGNodeAlias.
        """
        if self.src != self.report.from_g_node_alias:
            raise ValueError(
                f"Axiom 3 failed: src {self.src} must equal report.from_g_node_alias {self.report.from_g_node_alias}."
            )
        return self

    def upgrade(self) -> ReportEvent:
        """
        - Axioms: reinstate ReportIdentityPropagation, ReportCreatedTimePropagation and ReportSourcePropagation
        """
        data = self.model_dump()
        data["version"] = "004"
        return ReportEvent.model_validate(data)
