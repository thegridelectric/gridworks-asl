from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GwWeatherForecastFidelity
from sema.runtime.property_format import UtcIso8601Seconds
from sema.runtime.types.gw_weather_forecast_entry import GwWeatherForecastEntry


class GwWeatherForecast(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.forecast/000"""

    forecast_created: UtcIso8601Seconds
    fidelity: GwWeatherForecastFidelity
    forecasts: list[GwWeatherForecastEntry]
    type_name: Literal["gw.weather.forecast"] = "gw.weather.forecast"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwWeatherForecast":
        """
        Axiom 1: NonEmptyForecasts
        Forecasts SHALL be non-empty.
        """
        if len(self.forecasts) == 0:
            raise ValueError(
                "Axiom 1 (NonEmptyForecasts) failed: Forecasts must be non-empty."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwWeatherForecast":
        """
        Axiom 2: ChannelUniqueness
        No two elements of Forecasts SHALL share a ChannelName.
        """
        names = [f.channel_name for f in self.forecasts]
        if len(set(names)) != len(names):
            dupes = sorted({n for n in names if names.count(n) > 1})
            raise ValueError(
                "Axiom 2 (ChannelUniqueness) failed: Forecasts must not share "
                f"a ChannelName; duplicated: {dupes}."
            )
        return self
