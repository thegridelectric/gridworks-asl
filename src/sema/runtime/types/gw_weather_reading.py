from typing import Literal
from pydantic import StrictInt
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot


class GwWeatherReading(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.reading/000"""

    channel_name: LeftRightDot
    value: StrictInt
    type_name: Literal["gw.weather.reading"] = "gw.weather.reading"
    version: Literal["000"] = "000"
