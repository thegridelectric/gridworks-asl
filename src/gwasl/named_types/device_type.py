"""Type gw.device.type, version 000"""

from typing import Optional

from pydantic import BaseModel, ConfigDict
from gwasl.property_format import UUID4Str



class DeviceType(BaseModel):
    Id: UUID4Str
    DisplayName: Optional[str] = None
    Name: str
    TypeName: str = "device.type"
    Version: str = "000"

    model_config = ConfigDict(use_enum_values=True, extra="allow")

    