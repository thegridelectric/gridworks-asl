"""Type component.gt, version 001"""

from collections.abc import Sequence
from typing import Optional

from pydantic import BaseModel, field_validator

from gwasl.named_types.channel_config import ChannelConfig
from gwasl.property_format import UUID4Str


class ComponentGt(BaseModel):
    Id: UUID4Str
    DeviceTypeId: UUID4Str
    ConfigList: Sequence[ChannelConfig]
    DisplayName: Optional[str] = None
    HwUid: Optional[str] = None
    TypeName: str = "component.gt"
    Version: str = "002"

    @field_validator("ConfigList")
    @classmethod
    def check_config_list(cls, v: Sequence[ChannelConfig]) -> Sequence[ChannelConfig]:
        """
        Axiom 1: Channel Name uniqueness. Data Channel names are
        unique in the config list
        """
        # Implement Axiom(s)
        return v
