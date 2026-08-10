from typing import Literal
from pydantic import model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import UtcIso8601Seconds
from sema.runtime.types.gw_weather_reading import GwWeatherReading


class GwWeatherObservation(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.observation/000"""

    observation_time: UtcIso8601Seconds
    interpolated: bool
    readings: list[GwWeatherReading]
    type_name: Literal["gw.weather.observation"] = "gw.weather.observation"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwWeatherObservation":
        """
        Axiom 1: NonEmptyReadings
        Readings SHALL be non-empty.
        """
        if len(self.readings) == 0:
            raise ValueError(
                "Axiom 1 (NonEmptyReadings) failed: Readings must be non-empty."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwWeatherObservation":
        """
        Axiom 2: ChannelUniqueness
        No two elements of Readings SHALL share a ChannelName.
        """
        names = [r.channel_name for r in self.readings]
        if len(set(names)) != len(names):
            dupes = sorted({n for n in names if names.count(n) > 1})
            raise ValueError(
                "Axiom 2 (ChannelUniqueness) failed: Readings must not share "
                f"a ChannelName; duplicated: {dupes}."
            )
        return self
