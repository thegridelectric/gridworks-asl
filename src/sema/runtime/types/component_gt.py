from collections.abc import Sequence
from typing import Optional

from sema.runtime.base import SemaType
from pydantic import field_validator

from sema.runtime.types.channel_config import ChannelConfig
from sema.runtime.property_format import UUID4Str


class ComponentGt(SemaType):
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
