from typing import Literal

from sema.registry.base import SemaType
from pydantic import PositiveInt

from sema.registry.types.channel_readings import ChannelReadings
from sema.registry.types.machine_states import MachineStates
from sema.registry.property_format import (
    LeftRightDot,
    UTCMilliseconds,
    UTCSeconds,
    UUID4Str,
)


class Report(SemaType):
    FromGNodeAlias: LeftRightDot
    SlotStartUnixS: UTCSeconds
    SlotDurationS: PositiveInt
    ChannelReadingList: list[ChannelReadings]
    StateList: list[MachineStates]
    MessageCreatedMs: UTCMilliseconds
    Id: UUID4Str
    TypeName: Literal["report"] = "report"
    Version: str = "003"

