from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import TaValidationState
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class SlowContractRejection(SemaType):
    """Sema: https://schemas.electricity.works/types/slow.contract.rejection/000"""

    from_g_node_alias: LeftRightDot
    contract_id: UUID4Str
    validation_state: TaValidationState
    message_created_ms: UTCMilliseconds
    type_name: Literal["slow.contract.rejection"] = "slow.contract.rejection"
    version: Literal["000"] = "000"
