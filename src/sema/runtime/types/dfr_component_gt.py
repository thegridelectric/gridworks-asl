from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import PascalCase
from sema.runtime.property_format import PositiveInt
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.dfr_config import DfrConfig


class DfrComponentGt(SemaType):
    """Sema: https://schemas.electricity.works/types/dfr.component.gt/000"""

    component_id: UUID4Str
    device_type: PascalCase
    config_list: list[DfrConfig]
    i2c_address_list: list[PositiveInt]
    display_name: str | None = None
    hw_uid: str | None = None
    type_name: Literal["dfr.component.gt"] = "dfr.component.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "DfrComponentGt":
        """
        Axiom 1: ChannelNameUniqueness
        Channel names SHALL be unique across the ConfigList.
        """
        channel_names = [config.channel_name for config in self.config_list]
        if len(channel_names) != len(set(channel_names)):
            raise ValueError(
                "Axiom 1 (ChannelNameUniqueness) failed: channel names must be "
                "unique across the ConfigList."
            )
        return self
