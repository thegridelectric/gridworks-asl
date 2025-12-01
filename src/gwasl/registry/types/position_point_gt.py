from typing import Literal

from gwasl.registry.base import AslType
from pydantic import StrictInt, model_validator
from typing_extensions import Self

from gwasl.registry.property_format import UUID4Str


class PositionPointGt(AslType):
    """
    ASL type schema:
    [https://schemas.electricity.works/types/position.point.gt/000](https://schemas.electricity.works/types/position.point.gt/000)
    """
    id: UUID4Str
    latitude_micro_deg: StrictInt
    longitude_micro_deg: StrictInt
    type_name: Literal["position.point.gt"] = "position.point.gt"
    version: Literal["000"] = "000"

    @model_validator(mode="after") 
    def check_axiom_1(self) -> Self: 
        """
        Axiom 1: Coordinates must be valid Earth locations.
        Latitude: -90 to +90 degrees (-90,000,000 to +90,000,000 microdegrees)
        Longitude: -180 to +180 degrees (-180,000,000 to +180,000,000 microdegrees)
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

    @property
    def lat(self) -> float:
        """Get latitude in decimal degrees."""
        return self.latitude_micro_deg / 1_000_000

    @property
    def lon(self) -> float:
        """Get longitude in decimal degrees."""
        return self.longitude_micro_deg / 1_000_000