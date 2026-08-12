from typing import Literal
from sema.runtime.base import SemaType
from sema.runtime.types.gw_weather_channel_gt import GwWeatherChannelGt
from sema.runtime.types.gw_weather_forecast_bundle_gt import GwWeatherForecastBundleGt
from sema.runtime.types.gw_weather_forecast_channel_gt import GwWeatherForecastChannelGt
from sema.runtime.types.gw_weather_location_gt import GwWeatherLocationGt


class GwWeatherCreateCmd(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.create.cmd/000"""

    record: (
        GwWeatherChannelGt
        | GwWeatherForecastBundleGt
        | GwWeatherForecastChannelGt
        | GwWeatherLocationGt
    )
    proof: str | None = None
    type_name: Literal["gw.weather.create.cmd"] = "gw.weather.create.cmd"
    version: Literal["000"] = "000"
