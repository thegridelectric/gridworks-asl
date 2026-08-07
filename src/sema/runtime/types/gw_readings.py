from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.channel_readings import ChannelReadings
from sema.runtime.types.data_channel_gt import DataChannelGt
from sema.runtime.types.derived_channel_gt import DerivedChannelGt


class GwReadings(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.readings/000"""

    ta_alias: LeftRightDot
    start_unix_ms: UTCMilliseconds
    end_unix_ms: UTCMilliseconds
    channels: list[DataChannelGt | DerivedChannelGt]
    channel_readings_list: list[ChannelReadings]
    type_name: Literal["gw.readings"] = "gw.readings"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwReadings":
        """
        Axiom 1: WindowOrder
        EndUnixMs SHALL be greater than StartUnixMs.
        """
        if not self.end_unix_ms > self.start_unix_ms:
            raise ValueError(
                "Axiom 1 (WindowOrder) failed: EndUnixMs must be greater "
                "than StartUnixMs."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwReadings":
        """
        Axiom 2: ReadingsChannelCoverage
        Each ChannelReadingsList entry's ChannelName SHALL equal the Name
        of exactly one entry in Channels.
        """
        channel_names = [c.name for c in self.channels]
        for cr in self.channel_readings_list:
            if channel_names.count(cr.channel_name) != 1:
                raise ValueError(
                    "Axiom 2 (ReadingsChannelCoverage) failed: "
                    f"ChannelReadingsList entry {cr.channel_name!r} must "
                    "match exactly one Channels entry by Name."
                )
        return self
