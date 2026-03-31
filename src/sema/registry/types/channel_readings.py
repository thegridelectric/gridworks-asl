from typing import Literal

from pydantic import model_validator

from sema.registry.base import SemaType
from sema.registry.property_format import SpaceheatName, UTCMilliseconds


class ChannelReadings(SemaType):
    """Sema: https://schemas.electricity.works/types/channel.readings/002"""

    channel_name: SpaceheatName
    value_list: list[int]
    scada_read_time_unix_ms_list: list[UTCMilliseconds]
    type_name: Literal["channel.readings"] = "channel.readings"
    version: Literal["002"] = "002"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ChannelReadings":
        if len(self.value_list) != len(self.scada_read_time_unix_ms_list):
            raise ValueError(
                "Axiom 1 failed: value_list and scada_read_time_unix_ms_list must have equal length."
            )
        return self
