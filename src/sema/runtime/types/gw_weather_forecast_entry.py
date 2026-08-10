from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import UtcIso8601Seconds


class GwWeatherForecastEntry(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.forecast.entry/000"""

    channel_name: LeftRightDot
    first_slice_start: UtcIso8601Seconds
    values: list[StrictInt]
    type_name: Literal["gw.weather.forecast.entry"] = "gw.weather.forecast.entry"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwWeatherForecastEntry":
        """
        Axiom 1: NonEmptyValues
        Values SHALL be non-empty.
        """
        if len(self.values) == 0:
            raise ValueError(
                "Axiom 1 (NonEmptyValues) failed: Values must be non-empty."
            )
        return self
