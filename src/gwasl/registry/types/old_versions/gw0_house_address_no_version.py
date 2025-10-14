from typing import Literal
from gwasl.registry.codec import AslType
from gwasl.registry.types import Gw0HouseAddress

class Gw0HouseAddressNoVersion(AslType):
    street: str
    city: str
    state: str
    zip: str
    country: str
    latitude: float
    longitude: float
    type_name: Literal["gw0.house.address"] = "gw0.house.address"

    def to_latest(self) -> "Gw0HouseAddress":
        """Convert to the latest version."""
        return Gw0HouseAddress(
            street=self.street,
            city=self.city,
            state=self.state,
            zip=self.zip,
            country=self.country,
            latitude_micro_deg=int(self.latitude * 1_000_000),
            longitude_micro_deg=int(self.longitude * 1_000_000),
        )

