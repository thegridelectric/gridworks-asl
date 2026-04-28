from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName


class ChannelReadingsListItem(SemaType):
    """Sema: https://schemas.electricity.works/types/channel.readings.list.item/000"""

    channel_name: SpaceheatName
    value_list: list[StrictInt | None]
    unit: str
    unit_type: LeftRightDot
    type_name: Literal["channel.readings.list.item"] = "channel.readings.list.item"
    version: Literal["000"] = "000"
