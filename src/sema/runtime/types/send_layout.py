from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds


class SendLayout(SemaType):
    """Sema: https://schemas.electricity.works/types/send.layout/001"""

    from_g_node_alias: LeftRightDot
    message_created_ms: UTCMilliseconds
    type_name: Literal["send.layout"] = "send.layout"
    version: Literal["001"] = "001"
