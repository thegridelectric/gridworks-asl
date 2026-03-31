from typing import Literal

from sema.registry.enums.spaceheat_telemetry_name import SpaceheatTelemetryName
from sema.registry.property_format import LeftRightDot, SpaceheatName, UTCSeconds, UUID4Str
from sema.registry.types.data_channel_gt import DataChannelGt


class DataChannelGt001(DataChannelGt):
    """Sema: https://schemas.electricity.works/types/data.channel.gt/001"""

    telemetry_name: SpaceheatTelemetryName
    quantity: str | None = None
    type_name: Literal["data.channel.gt"] = "data.channel.gt"
    version: Literal["001"] = "001"
