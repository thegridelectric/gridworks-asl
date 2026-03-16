from typing import Literal
from pydantic import model_validator
from typing_extensions import Self
from gwasl.registry.codec import SemaType

class Gw0HouseAddress(SemaType):
    street: str
    city: str
    state: str
    zip: str
    country: str
    latitude_micro_deg: int
    longitude_micro_deg: int
    type_name: Literal["gw0.house.address"] = "gw0.house.address"
    version: Literal["000"] = "000"

    @model_validator(mode="after")
    def check_valid_earth_coordinates(self) -> Self:
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