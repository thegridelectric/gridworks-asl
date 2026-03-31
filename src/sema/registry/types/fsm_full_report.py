from typing import Literal

from sema.registry.base import SemaType
from sema.registry.property_format import SpaceheatName, UUID4Str
from sema.registry.types.fsm_atomic_report import FsmAtomicReport


class FsmFullReport(SemaType):
    """Sema: https://schemas.electricity.works/types/fsm.full.report/001"""

    from_name: SpaceheatName
    trigger_id: UUID4Str
    atomic_list: list[FsmAtomicReport]
    type_name: Literal["fsm.full.report"] = "fsm.full.report"
    version: Literal["001"] = "001"

    model_config = dict(SemaType.model_config)
    model_config["extra"] = "allow"
