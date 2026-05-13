from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds


class SendControlCapabilities(SemaType):
    """Sema: https://schemas.electricity.works/types/send.control.capabilities/000"""

    from_g_node_alias: LeftRightDot
    message_created_ms: UTCMilliseconds
    type_name: Literal["send.control.capabilities"] = "send.control.capabilities"
    version: Literal["000"] = "000"
