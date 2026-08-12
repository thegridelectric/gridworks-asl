from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.enums import GwWeatherForecastFidelity
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UTCMilliseconds
from sema.runtime.property_format import UtcIso8601Seconds


class GwWeatherForecast(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.forecast/000"""

    bundle_name: LeftRightDot
    source_updated_time: UtcIso8601Seconds
    message_created_ms: UTCMilliseconds
    fidelity: GwWeatherForecastFidelity
    first_slice_start: UtcIso8601Seconds
    temp_channel_name: LeftRightDot
    temp_values: list[StrictInt]
    wind_speed_channel_name: LeftRightDot
    wind_speed_values: list[StrictInt]
    type_name: Literal["gw.weather.forecast"] = "gw.weather.forecast"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwWeatherForecast":
        """
        Axiom 1: NonEmptyValues
        TempValues and WindSpeedValues SHALL be non-empty.
        """
        if len(self.temp_values) == 0 or len(self.wind_speed_values) == 0:
            raise ValueError(
                "Axiom 1 (NonEmptyValues) failed: TempValues and "
                "WindSpeedValues must be non-empty."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_2(self) -> "GwWeatherForecast":
        """
        Axiom 2: EqualValueLengths
        len(TempValues) SHALL equal len(WindSpeedValues).
        """
        if len(self.temp_values) != len(self.wind_speed_values):
            raise ValueError(
                "Axiom 2 (EqualValueLengths) failed: "
                f"len(TempValues)={len(self.temp_values)} must equal "
                f"len(WindSpeedValues)={len(self.wind_speed_values)}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_3(self) -> "GwWeatherForecast":
        """
        Axiom 3: DistinctChannels
        TempChannelName SHALL differ from WindSpeedChannelName.
        """
        if self.temp_channel_name == self.wind_speed_channel_name:
            raise ValueError(
                "Axiom 3 (DistinctChannels) failed: TempChannelName and "
                f"WindSpeedChannelName are both {self.temp_channel_name!r}."
            )
        return self

    @model_validator(mode="after")
    def check_axiom_4(self) -> "GwWeatherForecast":
        """
        Axiom 4: ForecastNaming
        a. BundleName SHALL contain "forecast" as an interior segment.
        b. TempChannelName SHALL contain "forecast" as an interior segment.
        c. WindSpeedChannelName SHALL contain "forecast" as an interior segment.
        """
        for label, value in (
            ("a", self.bundle_name),
            ("b", self.temp_channel_name),
            ("c", self.wind_speed_channel_name),
        ):
            if "forecast" not in value.split(".")[1:-1]:
                raise ValueError(
                    f"Axiom 4 (ForecastNaming, clause {label}) failed: "
                    f"{value!r} must contain 'forecast' as an interior "
                    "segment."
                )
        return self
