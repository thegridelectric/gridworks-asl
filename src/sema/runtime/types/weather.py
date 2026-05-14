from typing import Literal
from pydantic import StrictFloat
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCSeconds


class Weather(SemaType):
    """Sema: https://schemas.electricity.works/types/weather/000"""

    from_g_node_alias: LeftRightDot
    weather_channel_name: LeftRightDot
    unix_time_s: UTCSeconds
    outside_air_temp_f: StrictFloat
    wind_speed_mph: StrictFloat | None = None
    type_name: Literal["weather"] = "weather"
    version: Literal["000"] = "000"
