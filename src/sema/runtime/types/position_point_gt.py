from typing import Literal, Self
from pydantic import StrictInt, model_validator
from sema.runtime.base import SemaType
from sema.runtime.property_format import UUID4Str


class PositionPointGt(SemaType):
    """Sema: https://schemas.electricity.works/types/position.point.gt/000"""

    id: UUID4Str
    latitude_micro_deg: StrictInt
    longitude_micro_deg: StrictInt
    type_name: Literal["position.point.gt"] = "position.point.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after") 
    def check_axiom_1(self) -> Self: 
        """
        Axiom 1: ValidEarthCoordinates
        LatitudeMicroDeg SHALL be between -90,000,000 and 90,000,000 inclusive.
        LongitudeMicroDeg SHALL be between -180,000,000 and 180,000,000 inclusive.
        """
        if not -90_000_000 <= self.latitude_micro_deg <= 90_000_000:
            raise ValueError(
                f"Latitude {self.latitude_micro_deg / 1_000_000}° out of range [-90, 90]"
            )
        if not -180_000_000 <= self.longitude_micro_deg <= 180_000_000:
            raise ValueError(
                f"Longitude {self.longitude_micro_deg / 1_000_000}° out of range [-180, 180]"
            )
        return self
