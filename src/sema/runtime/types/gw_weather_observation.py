from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UtcIso8601Seconds


class GwWeatherObservation(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.observation/000"""

    location_alias: LeftRightDot
    observation_time: UtcIso8601Seconds
    interpolated: bool
    temp_channel_name: LeftRightDot
    temp_value: StrictInt
    wind_speed_channel_name: LeftRightDot
    wind_speed_value: StrictInt | None = None
    type_name: Literal["gw.weather.observation"] = "gw.weather.observation"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwWeatherObservation":
        """
        Axiom 1: DistinctChannels
        TempChannelName SHALL differ from WindSpeedChannelName.
        """
        if self.temp_channel_name == self.wind_speed_channel_name:
            raise ValueError(
                "Axiom 1 (DistinctChannels) failed: TempChannelName and "
                f"WindSpeedChannelName are both {self.temp_channel_name!r}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwWeatherObservation":
        """
        Axiom 2: LocationNaming
        a. TempChannelName SHALL begin with LocationAlias followed by ".".
        b. WindSpeedChannelName SHALL begin with LocationAlias followed by ".".
        """
        prefix = f"{self.location_alias}."
        for label, value in (
            ("a", self.temp_channel_name),
            ("b", self.wind_speed_channel_name),
        ):
            if not value.startswith(prefix):
                raise ValueError(
                    f"Axiom 2 (LocationNaming, clause {label}) failed: "
                    f"{value!r} must begin with {prefix!r}."
                )
        return self
