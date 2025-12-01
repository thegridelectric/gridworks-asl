from typing import Literal

from gwasl.registry.base import AslType
from pydantic import PositiveInt

from gwasl.registry.types.channel_readings import ChannelReadings
from gwasl.registry.types.machine_states import MachineStates
from gwasl.registry.property_format import (
    LeftRightDot,
    UTCMilliseconds,
    UTCSeconds,
    UUID4Str,
)


class Report(AslType):
    FromGNodeAlias: LeftRightDot
    SlotStartUnixS: UTCSeconds
    SlotDurationS: PositiveInt
    ChannelReadingList: list[ChannelReadings]
    StateList: list[MachineStates]
    MessageCreatedMs: UTCMilliseconds
    Id: UUID4Str
    TypeName: Literal["report"] = "report"
    Version: str = "003"

