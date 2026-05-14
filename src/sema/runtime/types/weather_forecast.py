from typing import Literal
from pydantic import StrictFloat, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCSeconds
from sema.runtime.property_format import UUID4Str


class WeatherForecast(SemaType):
    """Sema: https://schemas.electricity.works/types/weather.forecast/000"""

    from_g_node_alias: LeftRightDot
    weather_channel_name: LeftRightDot
    time: list[UTCSeconds]
    oat_f: list[StrictFloat]
    wind_speed_mph: list[StrictFloat]
    weather_uid: UUID4Str
    forecast_created_s: UTCSeconds
    type_name: Literal["weather.forecast"] = "weather.forecast"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "WeatherForecast":
        """
        Axiom 1: ListLengthConsistency
        Time, OatF, and WindSpeedMph SHALL all have the same length.
        """
        if len({len(self.time), len(self.oat_f), len(self.wind_speed_mph)}) > 1:
            raise ValueError(
                "Axiom 1 failed: time, oat_f, and wind_speed_mph must all have the same length."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "WeatherForecast":
        """
        Axiom 2: ForecastCreatedBeforeFirstInterval
        ForecastCreatedS SHALL be less than the first element of Time.
        """
        if self.time and self.forecast_created_s >= self.time[0]:
            raise ValueError(
                "Axiom 2 failed: forecast_created_s must be less than the first element of time."
            )
        return self
