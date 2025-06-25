"""Type data.channel.gt, version 001"""

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, model_validator
from typing_extensions import Self

from gwasl.enums import TelemetryName
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
    TelemetryName: TelemetryName
    TerminalAssetAlias: LeftRightDotStr
    InPowerMetering: Optional[bool] = None
    StartS: Optional[UTCSeconds] = None
    Id: UUID4Str
    TypeName: Literal["data.channel.gt"] = "data.channel.gt"
    Version: str = "001"

    @model_validator(mode="after")
    def check_axiom_1(self) -> Self:
        """
        Axiom 1: Power Metering.
        If InPowerMetering is true then the TelemetryName must be PowerW
        """
        if self.InPowerMetering and self.TelemetryName != TelemetryName.PowerW:
            raise ValueError(
                "Axiom 1 violated! If InPowerMetering is true then"
                f"the TelemetryName must be PowerW. Got  {self.TelemetryName}"
            )
        return self

    model_config = ConfigDict(use_enum_values=True)
