from typing import Literal

from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName, UUID4Str
from sema.runtime.types.old_versions.fsm_atomic_report_000 import FsmAtomicReport000
from sema.runtime.types.fsm_full_report import FsmFullReport

class FsmFullReport000(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.full.report/000"""

    from_name: SpaceheatName
    trigger_id: UUID4Str
    atomic_list: list[FsmAtomicReport000]
    type_name: Literal["fsm.full.report"] = "fsm.full.report"
    version: Literal["000"] = "000"

    model_config = dict(SemaType.model_config)
    model_config["extra"] = "allow"

    def upgrade(self) -> FsmFullReport:

        return FsmFullReport(
            from_name=self.from_name,
            trigger_id=self.trigger_id,
            atomic_list=[atomic.upgrade() for atomic in self.atomic_list],
        )
