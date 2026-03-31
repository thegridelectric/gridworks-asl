from typing import Literal

from sema.registry.base import SemaType
from sema.registry.property_format import SpaceheatName, UUID4Str
from sema.registry.types.old_versions.fsm_atomic_report_000 import FsmAtomicReport000


class FsmFullReport000(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.full.report/000"""

    from_name: SpaceheatName
    trigger_id: UUID4Str
    atomic_list: list[FsmAtomicReport000]
    type_name: Literal["fsm.full.report"] = "fsm.full.report"
    version: Literal["000"] = "000"

    model_config = dict(SemaType.model_config)
    model_config["extra"] = "allow"
