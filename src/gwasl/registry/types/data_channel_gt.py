"""Type data.channel.gt, version 010"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict
from gwasl.property_format import (
    LeftRightDotStr,
    SpaceheatName,
    UTCSeconds,
    UUID4Str,
)


class DataChannelGt(BaseModel):
    Name: SpaceheatName
    DisplayName: str
    AboutNodeName: SpaceheatName
    CapturedByNodeName: SpaceheatName
    TelemetryName: str
    TerminalAssetAlias: LeftRightDotStr
    InPowerMetering: Optional[bool] = None
    StartS: Optional[UTCSeconds] = None
    Id: UUID4Str
    ChannelVersion: Optional[str] = None
    TypeName: Literal["data.channel.gt"] = "data.channel.gt"
    Version: Literal["010"] = "010"


    model_config = ConfigDict(use_enum_values=True)
