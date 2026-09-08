from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.enums import GwScadaCmdRefusalReason
from sema.runtime.property_format import HandleName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class GwDispatchNack(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.dispatch.nack/000"""

    from_handle: HandleName
    to_handle: HandleName
    trigger_id: UUID4Str
    reason: GwScadaCmdRefusalReason
    unix_time_ms: UTCMilliseconds
    type_name: Literal["gw.dispatch.nack"] = "gw.dispatch.nack"
    version: Literal["000"] = "000"
