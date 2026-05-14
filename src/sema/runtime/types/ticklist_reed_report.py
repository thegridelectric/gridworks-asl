from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.ticklist_reed import TicklistReed


class TicklistReedReport(SemaType):
    """Sema: https://schemas.electricity.works/types/ticklist.reed.report/000"""

    terminal_asset_alias: LeftRightDot
    channel_name: SpaceheatName
    scada_received_unix_ms: UTCMilliseconds
    ticklist: TicklistReed
    type_name: Literal["ticklist.reed.report"] = "ticklist.reed.report"
    version: Literal["000"] = "000"
