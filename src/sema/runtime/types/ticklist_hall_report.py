from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import SpaceheatName
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.types.ticklist_hall import TicklistHall


class TicklistHallReport(SemaType):
    """Sema: https://schemas.electricity.works/types/ticklist.hall.report/000"""

    terminal_asset_alias: LeftRightDot
    channel_name: SpaceheatName
    scada_received_unix_ms: UTCMilliseconds
    ticklist: TicklistHall
    type_name: Literal["ticklist.hall.report"] = "ticklist.hall.report"
    version: Literal["000"] = "000"
