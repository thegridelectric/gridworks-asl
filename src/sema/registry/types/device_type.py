from typing import Optional

from sema.registry.base import SemaType, snake_to_pascal
from pydantic import ConfigDict
from sema.registry.property_format import UUID4Str


class DeviceType(SemaType):
    Id: UUID4Str
    DisplayName: Optional[str] = None
    Name: str
    TypeName: str = "device.type"
    Version: str = "000"

    model_config = ConfigDict(
        alias_generator=snake_to_pascal,
        frozen=True,
        populate_by_name=True,
        extra="allow",
    )

    