from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import HexChar
from sema.runtime.types.heartbeat_a import HeartbeatA


class HeartbeatA000(SemaType):
    """Sema: https://schemas.electricity.works/types/heartbeat.a/000"""

    my_hex: HexChar
    your_last_hex: HexChar | None = None
    type_name: Literal["heartbeat.a"] = "heartbeat.a"
    version: Literal["000"] = "000"

    def upgrade(self) -> HeartbeatA:
        """Minimal no-payload heartbeat variant."""
        data = []
        data["hp_turn_on_minutes"] = 12
        data["version"] = "006"
        return HeartbeatA.model_validate(data)
