from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot


class GridworksHeader(SemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.header/001"""

    src: str
    dst: str
    message_type: LeftRightDot
    message_id: str
    ack_required: bool
    type_name: Literal["gridworks.header"] = "gridworks.header"
    version: Literal["001"] = "001"
