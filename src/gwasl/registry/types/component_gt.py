from collections.abc import Sequence
from typing import Optional

from gwasl.registry.base import AslType
from pydantic import field_validator

from gwasl.registry.types.channel_config import ChannelConfig
from gwasl.registry.property_format import UUID4Str


class ComponentGt(AslType):
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
