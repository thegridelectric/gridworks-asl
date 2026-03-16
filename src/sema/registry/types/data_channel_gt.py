from typing import Literal, Optional

from sema.registry.base import SemaType
from sema.registry.property_format import (
    LeftRightDot,
    SpaceheatName,
    UTCSeconds,
    UUID4Str,
)


class DataChannelGt(SemaType):
    Name: SpaceheatName
    DisplayName: str
    AboutNodeName: SpaceheatName
    CapturedByNodeName: SpaceheatName
    TelemetryName: str
    TerminalAssetAlias: LeftRightDot
    InPowerMetering: Optional[bool] = None
    StartS: Optional[UTCSeconds] = None
    Id: UUID4Str
    ChannelVersion: Optional[str] = None
    TypeName: Literal["data.channel.gt"] = "data.channel.gt"
    Version: Literal["010"] = "010"
