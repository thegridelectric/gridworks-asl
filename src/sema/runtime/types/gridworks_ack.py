from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str


class GridworksAck(SemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.ack"""

    ack_message_i_d: UUID4Str
    type_name: Literal["gridworks.ack"] = "gridworks.ack"
