from typing import Literal
from pydantic import StrictFloat, model_validator
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

    @model_validator(mode="after")
    def check_axiom_1(self) -> "Weather":
        """
        Axiom 1: WindSpeedNonNegative
        If WindSpeedMph is present, it SHALL be greater than or equal to 0.
        """
        if self.wind_speed_mph is not None and self.wind_speed_mph < 0:
            raise ValueError(
                "Axiom 1 failed: WindSpeedMph must be >= 0 when present, "
                f"got {self.wind_speed_mph}."
            )
        return self
