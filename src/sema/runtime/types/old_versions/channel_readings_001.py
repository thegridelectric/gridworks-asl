from typing import Literal
from pydantic import ConfigDict, StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UUID4Str
from sema.runtime.types.channel_readings import ChannelReadings


class ChannelReadings001(SemaType):
    """Sema: https://schemas.electricity.works/types/channel.readings/001"""

    channel_name: SpaceheatName
    channel_id: UUID4Str
    value_list: list[StrictInt]
    scada_read_time_unix_ms_list: list[UTCMilliseconds]
    type_name: Literal["channel.readings"] = "channel.readings"
    version: Literal["001"] = "001"

    model_config = ConfigDict(**(SemaType.model_config | {"extra": "allow"}))

    @model_validator(mode="after")
    def check_axiom_1(self) -> "ChannelReadings001":
        """
        Axiom 1: ListLengthConsistency
        len(ValueList) SHALL equal len(ScadaReadTimeUnixMsList).
        """
        if len(self.value_list) != len(self.scada_read_time_unix_ms_list):
            raise ValueError(
                "Axiom 1 failed: value_list and scada_read_time_unix_ms_list must have equal length."
            )
        return self

    def upgrade(self) -> ChannelReadings:
        """
        - ChannelId: remove
        - additionalProperties: true -> false
        """
        data = self.model_dump()
        data.pop("channel_id", None)
        data["version"] = "002"
        return ChannelReadings.model_validate(data)
