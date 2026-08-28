from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class GridworksEventCommResponseTimeout(SemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.event.comm.response.timeout/001"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    peer_name: str
    type_name: Literal["gridworks.event.comm.response.timeout"] = (
        "gridworks.event.comm.response.timeout"
    )
    version: Literal["001"] = "001"
