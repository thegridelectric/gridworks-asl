from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str


class GridworksEventStartup(SemaType):
    """Sema: https://schemas.electricity.works/types/gridworks.event.startup"""

    message_id: UUID4Str
    time_created_ms: UTCMilliseconds
    src: LeftRightDot
    type_name: Literal["gridworks.event.startup"] = "gridworks.event.startup"
