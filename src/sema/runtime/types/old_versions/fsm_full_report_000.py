from typing import Literal
from pydantic import ConfigDict
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.fsm_full_report import FsmFullReport
from sema.runtime.types.old_versions.fsm_atomic_report_000 import FsmAtomicReport000


class FsmFullReport000(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.full.report/000"""

    from_name: SpaceheatName
    trigger_id: UUID4Str
    atomic_list: list[FsmAtomicReport000]
    type_name: Literal["fsm.full.report"] = "fsm.full.report"
    version: Literal["000"] = "000"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    def upgrade(self) -> FsmFullReport:
        """- AtomicList[]: fsm.atomic.report:000 -> 001"""
        data = self.model_dump()

        data["atomic_list"] = [atomic.upgrade() for atomic in self.atomic_list]

        data["version"] = "001"
        return FsmFullReport.model_validate(data)
