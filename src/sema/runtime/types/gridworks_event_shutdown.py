from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class GridworksEventShutdown(SemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.event.shutdown/001"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    reason: str
    type_name: Literal["gridworks.event.shutdown"] = "gridworks.event.shutdown"
    version: Literal["001"] = "001"
