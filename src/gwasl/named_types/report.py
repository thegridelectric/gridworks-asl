"""Type report, version 003"""

from typing import Literal

from pydantic import BaseModel, PositiveInt, field_validator

from gwasl.named_types.channel_readings import ChannelReadings
from gwasl.named_types.machine_states import MachineStates
from gwasl.property_format import (
    LeftRightDotStr,
    UTCMilliseconds,
    UTCSeconds,
    UUID4Str,
)


class Report(BaseModel):
    FromGNodeAlias: LeftRightDotStr
    SlotStartUnixS: UTCSeconds
    SlotDurationS: PositiveInt
    ChannelReadingList: list[ChannelReadings]
    StateList: list[MachineStates]
    MessageCreatedMs: UTCMilliseconds
    Id: UUID4Str
    TypeName: Literal["report"] = "report"
    Version: str = "003"

