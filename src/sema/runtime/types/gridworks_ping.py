from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str


class GridworksPing(SemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.ping"""

    message_id: UUID4Str
    type_name: Literal["gridworks.ping"] = "gridworks.ping"
