from typing import Literal
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import LeftRightDot
from sema.runtime.property_format import NonEmptyString
from sema.runtime.property_format import UUID4Str


class GwWeatherLocationGt(SemaType):
    """Sema: https://schemas.electricity.works/types/gw.weather.location.gt/000"""

    alias: LeftRightDot
    latitude_microdegrees: StrictInt
    longitude_microdegrees: StrictInt
    timezone: NonEmptyString
    icao_id: NonEmptyString | None = None
    wban_id: NonEmptyString | None = None
    ghcn_id: NonEmptyString | None = None
    coop_id: NonEmptyString | None = None
    id: UUID4Str
    type_name: Literal["gw.weather.location.gt"] = "gw.weather.location.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_axiom_1(self) -> "GwWeatherLocationGt":
        """
        Axiom 1: CoordinateBounds
        a. The absolute value of LatitudeMicrodegrees SHALL be at most 90000000.
        b. The absolute value of LongitudeMicrodegrees SHALL be at most 180000000.
        """
        if abs(self.latitude_microdegrees) > 90_000_000:
            raise ValueError(
                "Axiom 1 (CoordinateBounds) failed: a. |LatitudeMicrodegrees| "
                f"must be at most 90000000; got {self.latitude_microdegrees}."
            )
        if abs(self.longitude_microdegrees) > 180_000_000:
            raise ValueError(
                "Axiom 1 (CoordinateBounds) failed: b. |LongitudeMicrodegrees| "
                f"must be at most 180000000; got {self.longitude_microdegrees}."
            )
        return self
