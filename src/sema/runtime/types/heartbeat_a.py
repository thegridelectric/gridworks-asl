from typing import Literal
from sema.runtime.base import SemaType


class HeartbeatA(SemaType):
    """Sema: https://schemas.electricity.works/types/heartbeat.a/001"""

    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: Literal["001"] = "001"
